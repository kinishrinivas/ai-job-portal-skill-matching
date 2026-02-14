# app.py - Main Flask application entry point
# This is the file that starts the backend server
# Run with: python app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from config import Config
import os

# ===== CREATE FLASK APP =====

# Initialize Flask application
app = Flask(__name__)
# __name__ tells Flask the name of this module
# Flask uses this to find resources (templates, static files)

# Load configuration from Config class
app.config.from_object(Config)
# This loads all settings from config.py
# Now we can access them with app.config['SECRET_KEY']

# ===== SETUP CORS =====

# Enable CORS (Cross-Origin Resource Sharing)
# Allows React frontend (port 3000) to call Flask backend (port 5000)
CORS(app, origins=Config.CORS_ORIGINS)
# Without this, browser blocks frontend from calling backend

# ===== CONNECT TO MONGODB =====

try:
    # Create MongoDB client
    # This connects Python to MongoDB database
    mongo_client = MongoClient(Config.MONGO_URI)
    
    # Get the database
    db = mongo_client[Config.DATABASE_NAME]
    # Like selecting which filing cabinet to use
    
    # Test the connection
    mongo_client.server_info()
    # This throws error if connection fails
    
    print(f"✅ Connected to MongoDB database: {Config.DATABASE_NAME}")
    
except Exception as e:
    # If connection fails, print error and exit
    print(f"❌ Failed to connect to MongoDB: {e}")
    print("Make sure MongoDB is running and MONGO_URI is correct in .env file")
    db = None

# ===== DATABASE COLLECTIONS =====

# Get references to MongoDB collections
# Like getting references to different filing cabinets
users_collection = db['users'] if db is not None else None
jobs_collection = db['jobs'] if db is not None else None
applications_collection = db['applications'] if db is not None else None
resumes_collection = db['resumes'] if db is not None else None

# ===== CREATE UPLOAD FOLDER =====

# Create uploads folder if it doesn't exist
if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)
    print(f"✅ Created uploads folder: {Config.UPLOAD_FOLDER}")

# ===== BASIC ROUTES =====

@app.route('/')
def home():
    """
    Home route - test if server is running
    
    Visit: http://localhost:5000/
    
    Returns:
        JSON response with welcome message
    """
    return jsonify({
        "message": "Welcome to AI Job Portal API",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    """
    Health check route - test if database is connected
    
    Visit: http://localhost:5000/health
    
    Returns:
        JSON response with server and database status
    """
    # Check if database is connected
    db_status = "connected" if db is not None else "disconnected"
    
    return jsonify({
        "server": "running",
        "database": db_status,
        "timestamp": "2026-02-13"
    })

@app.route('/api/test')
def test_route():
    """
    Test route - verify API is working
    
    Visit: http://localhost:5000/api/test
    
    Returns:
        JSON response confirming API is accessible
    """
    return jsonify({
        "message": "API is working!",
        "cors_enabled": True,
        "upload_folder": Config.UPLOAD_FOLDER
    })

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors (page not found)
    
    Returns:
        JSON error message instead of HTML
    """
    return jsonify({
        "error": "Not Found",
        "message": "The requested URL was not found on this server"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 errors (server errors)
    
    Returns:
        JSON error message
    """
    return jsonify({
        "error": "Internal Server Error",
        "message": "Something went wrong on the server"
    }), 500

@app.errorhandler(413)
def too_large(error):
    """
    Handle 413 errors (file too large)
    
    Returns:
        JSON error message
    """
    return jsonify({
        "error": "File Too Large",
        "message": f"Maximum file size is {Config.MAX_CONTENT_LENGTH / (1024*1024)}MB"
    }), 413

# ===== REGISTER ROUTE BLUEPRINTS =====

# Import authentication routes
from routes.auth import auth_bp, init_auth_routes

# Import resume routes
from routes.resume import resume_bp, init_resume_routes

# Import job routes
from routes.job import job_bp, init_job_routes

# Initialize routes with database
init_auth_routes(db)
init_resume_routes(db)
init_job_routes(db)

# Register authentication blueprint
# All auth routes will be under /api/auth prefix
# Example: /api/auth/register, /api/auth/login, /api/auth/profile
app.register_blueprint(auth_bp, url_prefix='/api/auth')
print("✅ Registered authentication routes: /api/auth")

# Register resume blueprint
# All resume routes will be under /api/resume prefix
# Example: /api/resume/upload, /api/resume/my-resumes
app.register_blueprint(resume_bp, url_prefix='/api/resume')
print("✅ Registered resume routes: /api/resume")

# Register job blueprint
# All job routes will be under /api/jobs prefix
# Example: /api/jobs/create, /api/jobs/all, /api/jobs/<id>
app.register_blueprint(job_bp, url_prefix='/api/jobs')
print("✅ Registered job routes: /api/jobs")

# Future route blueprints will be added here
# from routes.matching import matching_bp
# 
# app.register_blueprint(matching_bp, url_prefix='/api/matching')

# ===== RUN THE APP =====

if __name__ == '__main__':
    """
    Start the Flask development server
    
    Only runs if this file is executed directly (python app.py)
    Does NOT run if this file is imported by another file
    """
    
    # Print startup message
    print("\n" + "="*50)
    print("🚀 AI Job Portal Backend Server")
    print("="*50)
    print(f"📡 Server running on: http://localhost:5000")
    print(f"🗄️  Database: {Config.DATABASE_NAME}")
    print(f"📁 Upload folder: {Config.UPLOAD_FOLDER}")
    print(f"🔧 Debug mode: {Config.DEBUG}")
    print("="*50 + "\n")
    
    # Start the server
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,       # Port 5000 (standard for Flask)
        debug=Config.DEBUG  # Enable debug mode from config
    )
    # debug=True: Auto-reloads when code changes (helpful in development)
    # host='0.0.0.0': Makes server accessible from other devices on network
