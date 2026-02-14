# resume.py - Resume upload and processing routes
# This file handles resume uploads, text extraction, and skill extraction

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from bson import ObjectId
import PyPDF2
import docx

from models.resume import Resume
from utils.skill_extractor import skill_extractor
from config import Config, allowed_file

# Create Blueprint for resume routes
resume_bp = Blueprint('resume', __name__)

# Database will be injected
db = None

def init_resume_routes(database):
    """Initialize resume routes with database connection"""
    global db
    db = database


def extract_text_from_pdf(file_path):
    """
    Extract text from PDF file
    
    Args:
        file_path (str): Path to PDF file
        
    Returns:
        str: Extracted text
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_path):
    """
    Extract text from DOCX file
    
    Args:
        file_path (str): Path to DOCX file
        
    Returns:
        str: Extracted text
    """
    try:
        doc = docx.Document(file_path)
        
        # Extract text from all paragraphs
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_file(file_path, file_type):
    """
    Extract text from resume file based on type
    
    Args:
        file_path (str): Path to file
        file_type (str): File extension (pdf, doc, docx)
        
    Returns:
        str: Extracted text
    """
    file_type = file_type.lower()
    
    if file_type == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type in ['doc', 'docx']:
        return extract_text_from_docx(file_path)
    else:
        raise Exception(f"Unsupported file type: {file_type}")


# ===== RESUME ROUTES =====

@resume_bp.route('/upload', methods=['POST'])
def upload_resume():
    """
    Upload and process resume file
    
    Requires authentication (student only)
    
    Request:
        - Multipart form data
        - File field: 'resume'
        - Must be PDF or DOCX
        
    Returns:
        JSON: Resume data with extracted skills
    """
    try:
        # Get user_id from request (in real app, get from JWT token)
        # For now, we'll accept it as form data
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Verify user exists and is a student
        user = db['users'].find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can upload resumes'}), 403
        
        # Check if file is present in request
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': 'Only PDF, DOC, and DOCX files are allowed'
            }), 400
        
        # Secure the filename
        # secure_filename removes dangerous characters
        original_filename = secure_filename(file.filename)
        
        # Create unique filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{user_id}_{timestamp}_{original_filename}"
        
        # Full file path
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Save file to uploads folder
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Get file extension
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        
        # Determine MIME type
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        file_type = mime_types.get(file_extension, 'application/octet-stream')
        
        # Create Resume object
        resume = Resume(
            student_id=user_id,
            file_name=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type
        )
        
        # Mark as processing
        resume.mark_processing()
        
        # Insert into database
        resume_dict = resume.to_dict()
        result = db['resumes'].insert_one(resume_dict)
        resume_id = result.inserted_id
        
        # ===== EXTRACT TEXT AND SKILLS =====
        
        try:
            # Extract text from file
            extracted_text = extract_text_from_file(file_path, file_extension)
            
            # Extract skills using AI
            skills = skill_extractor.extract_skills(extracted_text)
            
            # Extract other information
            email = skill_extractor.extract_email(extracted_text)
            phone = skill_extractor.extract_phone(extracted_text)
            education = skill_extractor.extract_education(extracted_text)
            experience_years = skill_extractor.extract_experience_years(extracted_text)
            
            # Calculate confidence
            confidence = skill_extractor.calculate_confidence(skills, len(extracted_text))
            
            # Update resume with extracted data
            db['resumes'].update_one(
                {'_id': resume_id},
                {
                    '$set': {
                        'extracted_text': extracted_text,
                        'extracted_skills': skills,
                        'extracted_email': email,
                        'extracted_phone': phone,
                        'extracted_education': education,
                        'parsing_status': 'completed',
                        'parsing_confidence': confidence,
                        'processed_at': datetime.utcnow()
                    }
                }
            )
            
            # Deactivate old resumes for this student
            db['resumes'].update_many(
                {
                    'student_id': ObjectId(user_id),
                    '_id': {'$ne': resume_id}  # Exclude current resume
                },
                {'$set': {'is_active': False}}
            )
            
            # Update user's student profile with skills
            db['users'].update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'student_profile.skills': skills,
                        'student_profile.resume_url': file_path,
                        'student_profile.education': education,
                        'student_profile.experience_years': experience_years
                    }
                }
            )
            
            # Return success response
            return jsonify({
                'message': 'Resume uploaded and processed successfully',
                'resume': {
                    'id': str(resume_id),
                    'file_name': original_filename,
                    'file_size': file_size,
                    'extracted_skills': skills,
                    'skills_count': len(skills),
                    'extracted_education': education,
                    'experience_years': experience_years,
                    'confidence': confidence,
                    'status': 'completed'
                }
            }), 201
            
        except Exception as e:
            # Mark resume as failed
            db['resumes'].update_one(
                {'_id': resume_id},
                {
                    '$set': {
                        'parsing_status': 'failed',
                        'parsing_error': str(e),
                        'processed_at': datetime.utcnow()
                    }
                }
            )
            
            return jsonify({
                'error': 'Resume uploaded but processing failed',
                'message': str(e),
                'resume_id': str(resume_id)
            }), 500
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@resume_bp.route('/my-resumes', methods=['GET'])
def get_my_resumes():
    """
    Get all resumes for current user
    
    Query Parameters:
        user_id (str): User ID (in real app, from JWT token)
        
    Returns:
        JSON: List of resumes
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Get all resumes for this user
        resumes = list(db['resumes'].find(
            {'student_id': ObjectId(user_id)},
            {'extracted_text': 0}  # Exclude large text field
        ).sort('uploaded_at', -1))  # Latest first
        
        # Convert ObjectId to string
        for resume in resumes:
            resume['_id'] = str(resume['_id'])
            resume['student_id'] = str(resume['student_id'])
        
        return jsonify({
            'resumes': resumes,
            'count': len(resumes)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get resumes: {str(e)}'}), 500


@resume_bp.route('/<resume_id>', methods=['GET'])
def get_resume(resume_id):
    """
    Get resume details by ID
    
    Args:
        resume_id (str): Resume ID
        
    Returns:
        JSON: Resume details
    """
    try:
        resume = db['resumes'].find_one({'_id': ObjectId(resume_id)})
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Convert ObjectId to string
        resume['_id'] = str(resume['_id'])
        resume['student_id'] = str(resume['student_id'])
        
        return jsonify({'resume': resume}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get resume: {str(e)}'}), 500


@resume_bp.route('/<resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    """
    Delete resume
    
    Args:
        resume_id (str): Resume ID
        
    Returns:
        JSON: Success message
    """
    try:
        # Get resume details
        resume = db['resumes'].find_one({'_id': ObjectId(resume_id)})
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Delete file from disk
        if os.path.exists(resume['file_path']):
            os.remove(resume['file_path'])
        
        # Delete from database
        db['resumes'].delete_one({'_id': ObjectId(resume_id)})
        
        return jsonify({'message': 'Resume deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete resume: {str(e)}'}), 500
