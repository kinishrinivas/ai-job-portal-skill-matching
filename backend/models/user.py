# user.py - Defines User model (Students, Companies, Admins)
# This file defines what fields a user document will have in MongoDB

from datetime import datetime
from bson import ObjectId

class User:
    """
    User model for all types of users
    
    Roles:
    - student: Can upload resume, apply to jobs
    - company: Can post jobs, view applications
    - admin: Can manage entire platform
    """
    
    def __init__(self, name, email, password, role, phone=None):
        """
        Initialize a new user
        
        Args:
            name (str): Full name of the user
            email (str): Email address (must be unique)
            password (str): Hashed password (NEVER store plain password!)
            role (str): "student", "company", or "admin"
            phone (str, optional): Phone number
        """
        self.name = name
        self.email = email
        self.password = password  # Will be hashed before saving
        self.role = role
        self.phone = phone
        self.created_at = datetime.utcnow()
        
        # Role-specific profiles (initialized as empty)
        self.student_profile = None
        self.company_profile = None
        
        # If student, create student profile structure
        if role == "student":
            self.student_profile = {
                "skills": [],           # Will be filled from resume
                "resume_url": None,     # Path to uploaded resume
                "education": None,
                "experience_years": 0,
                "location": None,
                "bio": None
            }
        
        # If company, create company profile structure
        elif role == "company":
            self.company_profile = {
                "company_name": None,
                "industry": None,
                "company_size": None,
                "website": None,
                "logo_url": None,
                "description": None,
                "location": None
            }
    
    def to_dict(self):
        """
        Convert user object to dictionary (for MongoDB storage)
        
        Returns:
            dict: User data as dictionary
        """
        user_dict = {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "phone": self.phone,
            "created_at": self.created_at
        }
        
        # Add role-specific profile if exists
        if self.student_profile:
            user_dict["student_profile"] = self.student_profile
        
        if self.company_profile:
            user_dict["company_profile"] = self.company_profile
        
        return user_dict
    
    @staticmethod
    def from_dict(data):
        """
        Create User object from dictionary (when reading from MongoDB)
        
        Args:
            data (dict): User data from database
            
        Returns:
            User: User object
        """
        user = User(
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password"),
            role=data.get("role"),
            phone=data.get("phone")
        )
        
        # Restore profiles if they exist
        if "student_profile" in data:
            user.student_profile = data["student_profile"]
        
        if "company_profile" in data:
            user.company_profile = data["company_profile"]
        
        if "created_at" in data:
            user.created_at = data["created_at"]
        
        return user
