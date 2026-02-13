# job.py - Defines Job model (Job postings by companies)
# This file defines what fields a job document will have in MongoDB

from datetime import datetime, timedelta
from bson import ObjectId

class Job:
    """
    Job model for job postings
    
    Only companies can create jobs
    Students can view and apply to jobs
    """
    
    def __init__(self, company_id, company_name, job_title, job_description, 
                 required_skills, job_type="Full-time", location="Remote"):
        """
        Initialize a new job posting
        
        Args:
            company_id (str): ID of the company posting this job
            company_name (str): Name of the company (for quick access)
            job_title (str): Job position title
            job_description (str): Detailed job description
            required_skills (list): List of required skills
            job_type (str): "Full-time", "Part-time", or "Internship"
            location (str): Job location or "Remote"
        """
        self.company_id = ObjectId(company_id) if isinstance(company_id, str) else company_id
        self.company_name = company_name
        self.company_logo = None  # Will be set from company profile
        
        self.job_title = job_title
        self.job_description = job_description
        self.job_type = job_type
        self.location = location
        
        # Skills
        self.required_skills = required_skills  # List like ["Python", "Flask"]
        self.optional_skills = []               # Nice-to-have skills
        
        # Requirements
        self.experience_required = None  # e.g., "2-5 years"
        self.education_required = None   # e.g., "Bachelor's in CS"
        
        # Salary
        self.salary_min = None
        self.salary_max = None
        self.currency = "INR"  # Default Indian Rupees
        
        # Metadata
        self.total_openings = 1
        self.applications_count = 0  # Tracks number of applications
        self.status = "active"       # "active", "closed", "draft"
        
        # Dates
        self.posted_date = datetime.utcnow()
        self.deadline = datetime.utcnow() + timedelta(days=30)  # Default 30 days
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """
        Convert job object to dictionary (for MongoDB storage)
        
        Returns:
            dict: Job data as dictionary
        """
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "company_logo": self.company_logo,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "job_type": self.job_type,
            "location": self.location,
            "required_skills": self.required_skills,
            "optional_skills": self.optional_skills,
            "experience_required": self.experience_required,
            "education_required": self.education_required,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
            "total_openings": self.total_openings,
            "applications_count": self.applications_count,
            "status": self.status,
            "posted_date": self.posted_date,
            "deadline": self.deadline,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        """
        Create Job object from dictionary (when reading from MongoDB)
        
        Args:
            data (dict): Job data from database
            
        Returns:
            Job: Job object
        """
        job = Job(
            company_id=data.get("company_id"),
            company_name=data.get("company_name"),
            job_title=data.get("job_title"),
            job_description=data.get("job_description"),
            required_skills=data.get("required_skills", []),
            job_type=data.get("job_type", "Full-time"),
            location=data.get("location", "Remote")
        )
        
        # Restore all other fields
        job.company_logo = data.get("company_logo")
        job.optional_skills = data.get("optional_skills", [])
        job.experience_required = data.get("experience_required")
        job.education_required = data.get("education_required")
        job.salary_min = data.get("salary_min")
        job.salary_max = data.get("salary_max")
        job.currency = data.get("currency", "INR")
        job.total_openings = data.get("total_openings", 1)
        job.applications_count = data.get("applications_count", 0)
        job.status = data.get("status", "active")
        job.posted_date = data.get("posted_date")
        job.deadline = data.get("deadline")
        job.created_at = data.get("created_at")
        job.updated_at = data.get("updated_at")
        
        return job
    
    def increment_applications(self):
        """
        Increment the applications count when someone applies
        """
        self.applications_count += 1
        self.updated_at = datetime.utcnow()
    
    def close_job(self):
        """
        Close the job (no more applications accepted)
        """
        self.status = "closed"
        self.updated_at = datetime.utcnow()
