# application.py - Defines Application model (Job applications by students)
# This file defines what happens when a student applies to a job

from datetime import datetime
from bson import ObjectId

class Application:
    """
    Application model for job applications
    
    Created when a student applies to a job
    Stores matching information and application status
    """
    
    def __init__(self, student_id, job_id, company_id, student_skills, 
                 job_required_skills, resume_url):
        """
        Initialize a new job application
        
        Args:
            student_id (str): ID of the student applying
            job_id (str): ID of the job being applied to
            company_id (str): ID of the company (job owner)
            student_skills (list): Student's skills from resume
            job_required_skills (list): Skills required by the job
            resume_url (str): Path to student's resume file
        """
        # IDs for relationships
        self.student_id = ObjectId(student_id) if isinstance(student_id, str) else student_id
        self.job_id = ObjectId(job_id) if isinstance(job_id, str) else job_id
        self.company_id = ObjectId(company_id) if isinstance(company_id, str) else company_id
        
        # Denormalized data (copied for quick access)
        self.student_name = None   # Will be filled from user data
        self.student_email = None
        self.job_title = None      # Will be filled from job data
        self.company_name = None
        
        # Resume
        self.resume_url = resume_url
        self.cover_letter = None   # Optional cover letter text
        
        # Skills data for matching
        self.student_skills = student_skills
        self.job_required_skills = job_required_skills
        
        # AI Matching results (will be calculated)
        self.match_score = 0.0              # Percentage match (0-100)
        self.matching_skills = []           # Skills that matched
        self.missing_skills = []            # Skills student doesn't have
        
        # Application status
        # Workflow: applied → shortlisted → interviewed → hired/rejected
        self.status = "applied"
        self.applied_date = datetime.utcnow()
        self.status_updated_at = datetime.utcnow()
        
        # Notes
        self.company_notes = ""    # Company can add private notes
        self.student_notes = ""    # Student can add application notes
    
    def calculate_match_score(self):
        """
        Calculate how well student's skills match job requirements
        
        Formula: (Matching Skills / Required Skills) * 100
        
        Example:
            Job requires: ["Python", "Flask", "MongoDB", "React"]  (4 skills)
            Student has: ["Python", "Flask", "JavaScript"]         (3 skills)
            Match: ["Python", "Flask"]                             (2 matching)
            Score: (2 / 4) * 100 = 50%
        """
        # Convert to lowercase for case-insensitive matching
        student_skills_lower = [skill.lower() for skill in self.student_skills]
        job_skills_lower = [skill.lower() for skill in self.job_required_skills]
        
        # Find matching skills
        matching = []
        missing = []
        
        for required_skill in self.job_required_skills:
            if required_skill.lower() in student_skills_lower:
                matching.append(required_skill)
            else:
                missing.append(required_skill)
        
        self.matching_skills = matching
        self.missing_skills = missing
        
        # Calculate percentage
        if len(self.job_required_skills) > 0:
            self.match_score = (len(matching) / len(self.job_required_skills)) * 100
        else:
            self.match_score = 0.0
        
        # Round to 2 decimal places
        self.match_score = round(self.match_score, 2)
    
    def to_dict(self):
        """
        Convert application object to dictionary (for MongoDB storage)
        
        Returns:
            dict: Application data as dictionary
        """
        return {
            "student_id": self.student_id,
            "job_id": self.job_id,
            "company_id": self.company_id,
            "student_name": self.student_name,
            "student_email": self.student_email,
            "job_title": self.job_title,
            "company_name": self.company_name,
            "resume_url": self.resume_url,
            "cover_letter": self.cover_letter,
            "student_skills": self.student_skills,
            "job_required_skills": self.job_required_skills,
            "match_score": self.match_score,
            "matching_skills": self.matching_skills,
            "missing_skills": self.missing_skills,
            "status": self.status,
            "applied_date": self.applied_date,
            "status_updated_at": self.status_updated_at,
            "company_notes": self.company_notes,
            "student_notes": self.student_notes
        }
    
    @staticmethod
    def from_dict(data):
        """
        Create Application object from dictionary (when reading from MongoDB)
        
        Args:
            data (dict): Application data from database
            
        Returns:
            Application: Application object
        """
        app = Application(
            student_id=data.get("student_id"),
            job_id=data.get("job_id"),
            company_id=data.get("company_id"),
            student_skills=data.get("student_skills", []),
            job_required_skills=data.get("job_required_skills", []),
            resume_url=data.get("resume_url")
        )
        
        # Restore all fields
        app.student_name = data.get("student_name")
        app.student_email = data.get("student_email")
        app.job_title = data.get("job_title")
        app.company_name = data.get("company_name")
        app.cover_letter = data.get("cover_letter")
        app.match_score = data.get("match_score", 0.0)
        app.matching_skills = data.get("matching_skills", [])
        app.missing_skills = data.get("missing_skills", [])
        app.status = data.get("status", "applied")
        app.applied_date = data.get("applied_date")
        app.status_updated_at = data.get("status_updated_at")
        app.company_notes = data.get("company_notes", "")
        app.student_notes = data.get("student_notes", "")
        
        return app
    
    def update_status(self, new_status):
        """
        Update application status
        
        Args:
            new_status (str): "applied", "shortlisted", "interviewed", "rejected", "hired"
        """
        self.status = new_status
        self.status_updated_at = datetime.utcnow()
