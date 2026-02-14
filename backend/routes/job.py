# job.py - Job Posting Routes
# Companies can create, edit, delete jobs
# Students can view and search jobs

from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from models.job import Job
from routes.auth import token_required
from config import Config

# Create blueprint
job_bp = Blueprint('job', __name__)

# Get database from app
db = None

def init_job_routes(database):
    """Initialize routes with database connection"""
    global db
    db = database


@job_bp.route('/create', methods=['POST'])
@token_required
def create_job(current_user):
    """
    Create a new job posting (Company only)
    
    Protected Route - Requires JWT token
    Only users with role='company' can create jobs
    
    Headers:
        Authorization: Bearer <token>
    
    Request Body (JSON):
        {
            "title": "Full Stack Developer",
            "description": "We are looking for...",
            "company_name": "Google India",
            "location": "Bangalore, India",
            "job_type": "Full-time",
            "experience_required": "2-5 years",
            "salary_min": 800000,
            "salary_max": 1500000,
            "required_skills": ["Python", "React", "MongoDB"],
            "application_deadline": "2024-12-31"
        }
    
    Returns:
        JSON: Success message and job ID
    """
    try:
        # Check if user is a company
        if current_user['role'] != 'company':
            return jsonify({'error': 'Only companies can post jobs'}), 403
        
        # Get job data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Required fields
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        company_name = data.get('company_name', '').strip()
        location = data.get('location', '').strip()
        required_skills = data.get('required_skills', [])
        
        # Validate required fields
        if not title:
            return jsonify({'error': 'Job title is required'}), 400
        
        if not description:
            return jsonify({'error': 'Job description is required'}), 400
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        if not required_skills or len(required_skills) == 0:
            return jsonify({'error': 'At least one required skill must be specified'}), 400
        
        # Optional fields with defaults
        job_type = data.get('job_type', 'Full-time')
        experience_required = data.get('experience_required', 'Not specified')
        salary_min = data.get('salary_min', 0)
        salary_max = data.get('salary_max', 0)
        application_deadline = data.get('application_deadline')
        
        # Parse deadline if provided
        deadline_date = None
        if application_deadline:
            try:
                deadline_date = datetime.strptime(application_deadline, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid deadline format. Use YYYY-MM-DD'}), 400
        
        # Create Job object
        job = Job(
            company_id=current_user['_id'],
            company_name=company_name,
            job_title=title,
            job_description=description,
            required_skills=required_skills,
            job_type=job_type,
            location=location
        )
        
        # Set optional fields
        if experience_required:
            job.experience_required = experience_required
        if salary_min:
            job.salary_min = salary_min
        if salary_max:
            job.salary_max = salary_max
        if deadline_date:
            job.deadline = deadline_date
        
        # Convert to dictionary
        job_dict = job.to_dict()
        
        # Insert into database
        result = db['jobs'].insert_one(job_dict)
        job_id = result.inserted_id
        
        return jsonify({
            'message': 'Job posted successfully',
            'job_id': str(job_id),
            'job': {
                'id': str(job_id),
                'job_title': title,
                'company_name': company_name,
                'location': location,
                'required_skills': required_skills,
                'status': 'active'
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create job: {str(e)}'}), 500


@job_bp.route('/all', methods=['GET'])
def get_all_jobs():
    """
    Get all active job postings
    
    Public route - No authentication required
    Students can browse all jobs
    
    Query Parameters (optional):
        ?location=Bangalore
        ?job_type=Full-time
        ?min_salary=500000
        ?skills=Python,React
    
    Returns:
        JSON: List of all active jobs
    """
    try:
        # Build filter query
        filter_query = {'status': 'active'}
        
        # Apply filters from query parameters
        location = request.args.get('location')
        if location:
            filter_query['location'] = {'$regex': location, '$options': 'i'}
        
        job_type = request.args.get('job_type')
        if job_type:
            filter_query['job_type'] = job_type
        
        min_salary = request.args.get('min_salary')
        if min_salary:
            filter_query['salary_min'] = {'$gte': int(min_salary)}
        
        skills = request.args.get('skills')
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            filter_query['required_skills'] = {'$in': skill_list}
        
        # Get jobs from database
        jobs = list(db['jobs'].find(filter_query).sort('posted_date', -1))
        
        # Convert ObjectId to string
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['company_id'] = str(job['company_id'])
            if job.get('posted_date'):
                job['posted_date'] = job['posted_date'].isoformat()
            if job.get('deadline'):
                job['deadline'] = job['deadline'].isoformat()
        
        return jsonify({
            'jobs': jobs,
            'total': len(jobs)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch jobs: {str(e)}'}), 500


@job_bp.route('/<job_id>', methods=['GET'])
def get_job_details(job_id):
    """
    Get details of a specific job
    
    Public route
    
    URL Parameter:
        job_id: Job ID
    
    Returns:
        JSON: Full job details
    """
    try:
        # Validate job_id
        if not ObjectId.is_valid(job_id):
            return jsonify({'error': 'Invalid job ID'}), 400
        
        # Find job
        job = db['jobs'].find_one({'_id': ObjectId(job_id)})
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Convert ObjectId to string
        job['_id'] = str(job['_id'])
        job['company_id'] = str(job['company_id'])
        if job.get('posted_date'):
            job['posted_date'] = job['posted_date'].isoformat()
        if job.get('deadline'):
            job['deadline'] = job['deadline'].isoformat()
        
        return jsonify({'job': job}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch job: {str(e)}'}), 500


@job_bp.route('/<job_id>/update', methods=['PUT'])
@token_required
def update_job(current_user, job_id):
    """
    Update a job posting (Company only - own jobs)
    
    Protected route - Requires JWT token
    
    Headers:
        Authorization: Bearer <token>
    
    URL Parameter:
        job_id: Job ID
    
    Request Body (JSON):
        {
            "title": "Updated Title",
            "description": "Updated description",
            "salary_max": 2000000
        }
    
    Returns:
        JSON: Success message
    """
    try:
        # Validate job_id
        if not ObjectId.is_valid(job_id):
            return jsonify({'error': 'Invalid job ID'}), 400
        
        # Find job
        job = db['jobs'].find_one({'_id': ObjectId(job_id)})
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if user is the owner
        if str(job['company_id']) != str(current_user['_id']):
            return jsonify({'error': 'You can only update your own jobs'}), 403
        
        # Get update data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Allowed fields to update
        update_fields = {}
        
        if 'title' in data:
            update_fields['job_title'] = data['title'].strip()
        
        if 'description' in data:
            update_fields['job_description'] = data['description'].strip()
        
        if 'location' in data:
            update_fields['location'] = data['location'].strip()
        
        if 'job_type' in data:
            update_fields['job_type'] = data['job_type']
        
        if 'experience_required' in data:
            update_fields['experience_required'] = data['experience_required']
        
        if 'salary_min' in data:
            update_fields['salary_min'] = data['salary_min']
        
        if 'salary_max' in data:
            update_fields['salary_max'] = data['salary_max']
        
        if 'required_skills' in data:
            if len(data['required_skills']) == 0:
                return jsonify({'error': 'At least one required skill must be specified'}), 400
            update_fields['required_skills'] = data['required_skills']
        
        if 'application_deadline' in data:
            try:
                update_fields['deadline'] = datetime.strptime(
                    data['application_deadline'], '%Y-%m-%d'
                )
            except ValueError:
                return jsonify({'error': 'Invalid deadline format. Use YYYY-MM-DD'}), 400
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update job
        db['jobs'].update_one(
            {'_id': ObjectId(job_id)},
            {'$set': update_fields}
        )
        
        return jsonify({
            'message': 'Job updated successfully',
            'updated_fields': list(update_fields.keys())
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update job: {str(e)}'}), 500


@job_bp.route('/<job_id>/delete', methods=['DELETE'])
@token_required
def delete_job(current_user, job_id):
    """
    Delete a job posting (Company only - own jobs)
    
    Protected route - Requires JWT token
    
    Headers:
        Authorization: Bearer <token>
    
    URL Parameter:
        job_id: Job ID
    
    Returns:
        JSON: Success message
    """
    try:
        # Validate job_id
        if not ObjectId.is_valid(job_id):
            return jsonify({'error': 'Invalid job ID'}), 400
        
        # Find job
        job = db['jobs'].find_one({'_id': ObjectId(job_id)})
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if user is the owner
        if str(job['company_id']) != str(current_user['_id']):
            return jsonify({'error': 'You can only delete your own jobs'}), 403
        
        # Delete job
        db['jobs'].delete_one({'_id': ObjectId(job_id)})
        
        return jsonify({
            'message': 'Job deleted successfully',
            'job_id': job_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete job: {str(e)}'}), 500


@job_bp.route('/<job_id>/close', methods=['PUT'])
@token_required
def close_job(current_user, job_id):
    """
    Close a job posting (stop accepting applications)
    
    Protected route - Requires JWT token
    
    Headers:
        Authorization: Bearer <token>
    
    URL Parameter:
        job_id: Job ID
    
    Returns:
        JSON: Success message
    """
    try:
        # Validate job_id
        if not ObjectId.is_valid(job_id):
            return jsonify({'error': 'Invalid job ID'}), 400
        
        # Find job
        job = db['jobs'].find_one({'_id': ObjectId(job_id)})
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if user is the owner
        if str(job['company_id']) != str(current_user['_id']):
            return jsonify({'error': 'You can only close your own jobs'}), 403
        
        # Close job
        db['jobs'].update_one(
            {'_id': ObjectId(job_id)},
            {'$set': {'status': 'closed'}}
        )
        
        return jsonify({
            'message': 'Job closed successfully',
            'job_id': job_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to close job: {str(e)}'}), 500


@job_bp.route('/my-jobs', methods=['GET'])
@token_required
def get_my_jobs(current_user):
    """
    Get all jobs posted by current company
    
    Protected route - Requires JWT token
    Only for companies
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: List of jobs posted by this company
    """
    try:
        # Check if user is a company
        if current_user['role'] != 'company':
            return jsonify({'error': 'Only companies can access this route'}), 403
        
        # Get all jobs by this company
        jobs = list(db['jobs'].find({'company_id': current_user['_id']}).sort('posted_date', -1))
        
        # Convert ObjectId to string
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['company_id'] = str(job['company_id'])
            if job.get('posted_date'):
                job['posted_date'] = job['posted_date'].isoformat()
            if job.get('deadline'):
                job['deadline'] = job['deadline'].isoformat()
        
        return jsonify({
            'jobs': jobs,
            'total': len(jobs)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch jobs: {str(e)}'}), 500
