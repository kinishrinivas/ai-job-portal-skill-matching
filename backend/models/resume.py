# resume.py - Defines Resume model (Resume metadata and AI extraction results)
# This file stores information about uploaded resumes and extracted data

from datetime import datetime
from bson import ObjectId

class Resume:
    """
    Resume model for storing resume files and AI-extracted information
    
    When a student uploads a resume:
    1. File is saved to /uploads folder
    2. AI extracts text, skills, education, experience
    3. This data is stored in MongoDB for quick access
    """
    
    def __init__(self, student_id, file_name, file_path, file_size, file_type):
        """
        Initialize a new resume record
        
        Args:
            student_id (str): ID of the student who uploaded
            file_name (str): Original filename (e.g., "john_resume.pdf")
            file_path (str): Server path where file is saved
            file_size (int): File size in bytes
            file_type (str): MIME type (e.g., "application/pdf")
        """
        self.student_id = ObjectId(student_id) if isinstance(student_id, str) else student_id
        
        # File information
        self.file_name = file_name
        self.file_path = file_path
        self.file_size = file_size
        self.file_type = file_type
        
        # Extracted content (filled by AI after processing)
        self.extracted_text = None     # Full text extracted from PDF/DOC
        self.extracted_skills = []     # List of skills found by AI
        self.extracted_education = None
        self.extracted_experience = []  # List of job experiences
        self.extracted_email = None
        self.extracted_phone = None
        
        # Processing status
        # Workflow: pending → processing → completed/failed
        self.parsing_status = "pending"
        self.parsing_confidence = 0.0  # How confident AI is (0-100)
        self.parsing_error = None      # Error message if parsing fails
        
        # Version control (if student uploads multiple times)
        self.version = 1
        self.is_active = True  # Only latest resume is active
        
        # Timestamps
        self.uploaded_at = datetime.utcnow()
        self.processed_at = None  # Set when AI finishes processing
    
    def to_dict(self):
        """
        Convert resume object to dictionary (for MongoDB storage)
        
        Returns:
            dict: Resume data as dictionary
        """
        return {
            "student_id": self.student_id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "extracted_text": self.extracted_text,
            "extracted_skills": self.extracted_skills,
            "extracted_education": self.extracted_education,
            "extracted_experience": self.extracted_experience,
            "extracted_email": self.extracted_email,
            "extracted_phone": self.extracted_phone,
            "parsing_status": self.parsing_status,
            "parsing_confidence": self.parsing_confidence,
            "parsing_error": self.parsing_error,
            "version": self.version,
            "is_active": self.is_active,
            "uploaded_at": self.uploaded_at,
            "processed_at": self.processed_at
        }
    
    @staticmethod
    def from_dict(data):
        """
        Create Resume object from dictionary (when reading from MongoDB)
        
        Args:
            data (dict): Resume data from database
            
        Returns:
            Resume: Resume object
        """
        resume = Resume(
            student_id=data.get("student_id"),
            file_name=data.get("file_name"),
            file_path=data.get("file_path"),
            file_size=data.get("file_size"),
            file_type=data.get("file_type")
        )
        
        # Restore extracted data
        resume.extracted_text = data.get("extracted_text")
        resume.extracted_skills = data.get("extracted_skills", [])
        resume.extracted_education = data.get("extracted_education")
        resume.extracted_experience = data.get("extracted_experience", [])
        resume.extracted_email = data.get("extracted_email")
        resume.extracted_phone = data.get("extracted_phone")
        
        # Restore status
        resume.parsing_status = data.get("parsing_status", "pending")
        resume.parsing_confidence = data.get("parsing_confidence", 0.0)
        resume.parsing_error = data.get("parsing_error")
        resume.version = data.get("version", 1)
        resume.is_active = data.get("is_active", True)
        
        # Restore timestamps
        resume.uploaded_at = data.get("uploaded_at")
        resume.processed_at = data.get("processed_at")
        
        return resume
    
    def set_extracted_data(self, skills, education=None, experience=None, 
                          email=None, phone=None, full_text=None):
        """
        Set the AI-extracted data
        
        Args:
            skills (list): List of extracted skills
            education (str, optional): Education details
            experience (list, optional): Work experience list
            email (str, optional): Extracted email
            phone (str, optional): Extracted phone
            full_text (str, optional): Full extracted text
        """
        self.extracted_skills = skills
        self.extracted_education = education
        self.extracted_experience = experience or []
        self.extracted_email = email
        self.extracted_phone = phone
        self.extracted_text = full_text
        self.parsing_status = "completed"
        self.processed_at = datetime.utcnow()
    
    def mark_processing(self):
        """
        Mark resume as being processed by AI
        """
        self.parsing_status = "processing"
    
    def mark_failed(self, error_message):
        """
        Mark resume parsing as failed
        
        Args:
            error_message (str): Error description
        """
        self.parsing_status = "failed"
        self.parsing_error = error_message
        self.processed_at = datetime.utcnow()
    
    def deactivate(self):
        """
        Deactivate this resume (when student uploads a new one)
        """
        self.is_active = False
