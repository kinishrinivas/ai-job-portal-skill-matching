# test_resume.py - Test resume upload and skill extraction
# This file demonstrates how to upload resumes and extract skills

import requests
import json

# Base URL
BASE_URL = "http://localhost:5000/api"

def test_resume_upload():
    """Test resume upload with a real file"""
    print("\n" + "="*50)
    print("TEST: Resume Upload & Skill Extraction")
    print("="*50)
    
    # First, register a student or get existing student ID
    print("\n1. Creating a test student account...")
    
    # Register student
    register_data = {
        "name": "Alice Johnson",
        "email": "alice@student.com",
        "password": "Alice@123",
        "role": "student",
        "phone": "+919876543333"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    if response.status_code == 201:
        user_data = response.json()
        user_id = user_data['user']['id']
        print(f"✅ Student created: {user_data['user']['name']}")
        print(f"   User ID: {user_id}")
    elif response.status_code == 409:
        # User already exists, login instead
        print("   Student already exists, logging in...")
        login_data = {
            "email": "alice@student.com",
            "password": "Alice@123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        user_data = response.json()
        user_id = user_data['user']['id']
        print(f"✅ Logged in: {user_data['user']['name']}")
        print(f"   User ID: {user_id}")
    else:
        print(f"❌ Failed to create/login student: {response.json()}")
        return
    
    # Create a sample resume file
    print("\n2. Creating sample resume file...")
    create_sample_resume()
    print("✅ Sample resume created: sample_resume.txt")
    
    # Upload resume
    print("\n3. Uploading resume...")
    
    with open('sample_resume.txt', 'rb') as resume_file:
        files = {'resume': ('alice_johnson_resume.txt', resume_file, 'text/plain')}
        data = {'user_id': user_id}
        
        response = requests.post(
            f"{BASE_URL}/resume/upload",
            files=files,
            data=data
        )
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        result = response.json()
        print("\n✅ RESUME UPLOADED SUCCESSFULLY!")
        print(f"   Skills Found: {result['resume']['skills_count']}")
        print(f"   Skills: {', '.join(result['resume']['extracted_skills'])}")
        print(f"   Education: {result['resume']['extracted_education']}")
        print(f"   Experience: {result['resume']['experience_years']} years")
        print(f"   Confidence: {result['resume']['confidence']}%")
        
        resume_id = result['resume']['id']
        
        # Get user profile to verify skills were added
        print("\n4. Checking updated user profile...")
        response = requests.get(
            f"{BASE_URL}/auth/profile",
            headers={'Authorization': f"Bearer {user_data['token']}"}
        )
        
        if response.status_code == 200:
            profile = response.json()['user']
            print(f"✅ Profile updated with skills:")
            print(f"   {', '.join(profile['student_profile']['skills'])}")
        
        # Get resume details
        print("\n5. Fetching resume details...")
        response = requests.get(f"{BASE_URL}/resume/{resume_id}")
        
        if response.status_code == 200:
            resume = response.json()['resume']
            print(f"✅ Resume details retrieved")
            print(f"   File: {resume['file_name']}")
            print(f"   Size: {resume['file_size']} bytes")
            print(f"   Status: {resume['parsing_status']}")
        
        return resume_id
    else:
        print("❌ Resume upload failed!")
        return None


def create_sample_resume():
    """Create a sample resume text file"""
    resume_content = """
ALICE JOHNSON
Email: alice.johnson@email.com
Phone: +1-234-567-8901

SUMMARY
Experienced Full-Stack Developer with 3 years of experience in building web applications
using modern technologies. Proficient in Python, JavaScript, React, and MongoDB.

EDUCATION
Bachelor of Technology in Computer Science
ABC University, 2021

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, Java, C++
Web Technologies: React, Node.js, Express.js, HTML, CSS, Bootstrap
Databases: MongoDB, MySQL, PostgreSQL
Cloud & DevOps: AWS, Docker, Git, GitHub
Frameworks: Flask, Django, REST API

PROFESSIONAL EXPERIENCE

Software Developer - XYZ Tech Solutions (2021-2024)
- Developed full-stack web applications using React and Flask
- Implemented RESTful APIs with Python Flask backend
- Worked with MongoDB for database management
- Deployed applications on AWS cloud platform
- Collaborated with team using Git and Agile methodologies

PROJECTS

E-Commerce Platform
- Built a full-stack e-commerce application using React, Node.js, and MongoDB
- Implemented user authentication with JWT
- Created responsive UI with Bootstrap and CSS

Task Management System
- Developed a task management tool using Python Flask and PostgreSQL
- Integrated real-time updates using WebSockets
- Deployed on Docker containers

CERTIFICATIONS
- AWS Certified Developer Associate
- MongoDB Certified Developer

LANGUAGES
- English (Fluent)
- Hindi (Native)
"""
    
    with open('sample_resume.txt', 'w', encoding='utf-8') as f:
        f.write(resume_content)


def test_get_my_resumes(user_id):
    """Test getting all resumes for a user"""
    print("\n" + "="*50)
    print("TEST: Get My Resumes")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/resume/my-resumes?user_id={user_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['count']} resume(s)")
        for resume in result['resumes']:
            print(f"\n   Resume: {resume['file_name']}")
            print(f"   Skills: {', '.join(resume.get('extracted_skills', []))}")
            print(f"   Uploaded: {resume['uploaded_at']}")
    else:
        print("❌ Failed to get resumes")


# Run tests
if __name__ == "__main__":
    print("\n🧪 RESUME UPLOAD & SKILL EXTRACTION TESTS")
    print("="*50)
    print("Make sure Flask server is running on http://localhost:5000")
    print("="*50)
    
    try:
        # Test resume upload
        resume_id = test_resume_upload()
        
        if resume_id:
            # Note: In a real app, we'd get user_id from JWT token
            # For testing, we'll use the ID from registration
            # test_get_my_resumes(user_id)
            pass
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETED!")
        print("="*50)
        print("\nNext: Check MongoDB Atlas to see:")
        print("  - resumes collection with extracted data")
        print("  - users collection with updated student_profile.skills")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure Flask server is running: python backend/app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
