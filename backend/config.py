# config.py - Configuration settings for the Flask application
# This file stores all settings like database URL, secret keys, etc.

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
# .env file stores sensitive data like passwords (NOT committed to Git)
load_dotenv()

class Config:
    """
    Configuration class for Flask application
    
    All settings are stored here in one place
    Makes it easy to change settings without touching code
    """
    
    # ===== FLASK SETTINGS =====
    
    # Secret key for encrypting session data and JWT tokens
    # MUST be random and secret! Like a master password
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    # os.getenv() reads from .env file
    # Second parameter is default value (used if .env doesn't have it)
    
    # Enable/disable debug mode
    # Debug mode shows detailed errors (helpful during development)
    # MUST be False in production (for security)
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # ===== DATABASE SETTINGS =====
    
    # MongoDB connection string
    # Format: mongodb+srv://username:password@cluster.mongodb.net/database_name
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/job_portal_db')
    # Default connects to local MongoDB (for development)
    # In production, use MongoDB Atlas URL from .env file
    
    # Database name
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'job_portal_db')
    
    # ===== JWT SETTINGS =====
    
    # JWT token expiration time
    # How long before user needs to login again
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # 24 hours
    # timedelta is like setting an alarm for 24 hours
    
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 30 days
    # Refresh token lasts longer - for "Remember Me" feature
    
    # JWT algorithm for encryption
    JWT_ALGORITHM = 'HS256'  # Standard algorithm
    
    # ===== FILE UPLOAD SETTINGS =====
    
    # Folder where uploaded files (resumes) are stored
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    # os.path.join() creates correct path for any OS (Windows/Mac/Linux)
    # __file__ means "this file's location"
    # Result: C:\...\backend\uploads
    
    # Maximum file size: 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB in bytes
    # 5 * 1024 * 1024 = 5,242,880 bytes = 5 MB
    # Why? Large resumes slow down upload and use storage
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    # Only these file types can be uploaded
    # Security: prevents uploading .exe, .js, etc.
    
    # ===== CORS SETTINGS =====
    
    # Allowed origins (which websites can call our API)
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    # Frontend runs on port 3000, backend on port 5000
    # CORS allows them to communicate
    # Can add multiple: 'http://localhost:3000,https://myapp.com'
    
    # ===== AI/NLP SETTINGS =====
    
    # Minimum confidence score for skill extraction
    # If AI is less than 60% confident, ignore that skill
    MIN_SKILL_CONFIDENCE = 0.6  # 60%
    
    # Predefined skill database (for matching)
    # We'll use this to validate extracted skills
    # Full list will be longer - this is just examples
    KNOWN_SKILLS = [
        # Programming Languages
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 
        'TypeScript', 'Swift', 'Kotlin', 'Rust', 'Scala', 'R',
        
        # Web Frameworks
        'React', 'Angular', 'Vue.js', 'Flask', 'Django', 'Express.js', 
        'Spring Boot', 'ASP.NET', 'Laravel', 'Ruby on Rails',
        
        # Databases
        'MongoDB', 'MySQL', 'PostgreSQL', 'SQLite', 'Redis', 'Oracle',
        'SQL Server', 'Cassandra', 'DynamoDB', 'Firebase',
        
        # Cloud & DevOps
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
        'Git', 'GitHub', 'GitLab', 'CI/CD', 'Terraform',
        
        # AI/ML
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
        'NLP', 'Computer Vision', 'scikit-learn', 'Keras',
        
        # Other
        'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum',
        'HTML', 'CSS', 'Bootstrap', 'Tailwind CSS', 'Node.js'
    ]
    
    # ===== EMAIL SETTINGS (Optional - for future features) =====
    
    # Email configuration for sending notifications
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # ===== PAGINATION SETTINGS =====
    
    # Number of jobs to show per page
    JOBS_PER_PAGE = 10
    
    # Number of applications to show per page
    APPLICATIONS_PER_PAGE = 20
    
    # ===== SECURITY SETTINGS =====
    
    # Bcrypt work factor (higher = more secure but slower)
    # 12 is a good balance between security and speed
    BCRYPT_LOG_ROUNDS = 12

# Helper function to check if file extension is allowed
def allowed_file(filename):
    """
    Check if uploaded file has allowed extension
    
    Args:
        filename (str): Name of the uploaded file
        
    Returns:
        bool: True if allowed, False otherwise
        
    Example:
        allowed_file('resume.pdf') → True
        allowed_file('virus.exe') → False
    """
    # Check if filename has a dot AND extension is in ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    # rsplit('.', 1) splits from right: 'resume.pdf' → ['resume', 'pdf']
    # [1] gets the extension part
    # .lower() converts to lowercase (PDF → pdf)
