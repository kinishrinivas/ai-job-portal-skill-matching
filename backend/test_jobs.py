# test_jobs.py - Test job posting endpoints
# This demonstrates how companies can post, edit, and delete jobs
# And how students can browse and view jobs

import requests
import json

BASE_URL = "http://localhost:5000/api"

# Store tokens and IDs globally
company_token = None
student_token = None
job_id = None

def test_register_company():
    """Test company registration or login"""
    print("\n" + "="*60)
    print("TEST 1: Login Company (TCS)")
    print("="*60)
    
    # Try to login first
    login_data = {
        "email": "recruiter@tcs.com",
        "password": "Tcs@123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        global company_token
        company_token = response.json()['token']
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Company logged in successfully!")
        print(f"🔑 Token saved: {company_token[:50]}...")
        return company_token
    
    # If login fails, try to register
    print("Login failed, registering new company...")
    data = {
        "name": "TCS Recruiter",
        "email": "recruiter@tcs.com",
        "password": "Tcs@123456",
        "role": "company",
        "phone": "+919876543210"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        company_token = response.json()['token']
        print("✅ Company registered successfully!")
        print(f"🔑 Token saved: {company_token[:50]}...")
        return company_token
    else:
        print("❌ Company registration/login failed!")
        return None


def test_register_student():
    """Test student registration"""
    print("\n" + "="*60)
    print("TEST 2: Register Student (Bob)")
    print("="*60)
    
    data = {
        "name": "Bob Smith",
        "email": "bob@student.com",
        "password": "Student@123",
        "role": "student",
        "phone": "+919876543211"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        global student_token
        student_token = response.json()['token']
        print("✅ Student registered successfully!")
        print(f"🔑 Token saved: {student_token[:50]}...")
        return student_token
    else:
        print("❌ Student registration failed!")
        return None


def test_create_job_without_auth():
    """Test creating job without authentication (should fail)"""
    print("\n" + "="*60)
    print("TEST 3: Create Job WITHOUT Token (Should Fail)")
    print("="*60)
    
    data = {
        "title": "Full Stack Developer",
        "description": "Looking for an experienced developer",
        "company_name": "TCS",
        "location": "Bangalore",
        "required_skills": ["Python", "React"]
    }
    
    # No Authorization header
    response = requests.post(f"{BASE_URL}/jobs/create", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✅ Correctly rejected - Authentication required!")
    else:
        print("❌ Should have returned 401 Unauthorized")


def test_create_job_as_student():
    """Test creating job as student (should fail - only companies allowed)"""
    print("\n" + "="*60)
    print("TEST 4: Create Job as STUDENT (Should Fail)")
    print("="*60)
    
    data = {
        "title": "Full Stack Developer",
        "description": "Looking for an experienced developer",
        "company_name": "TCS",
        "location": "Bangalore",
        "required_skills": ["Python", "React"]
    }
    
    # Use student token (wrong role)
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.post(f"{BASE_URL}/jobs/create", json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 403:
        print("✅ Correctly rejected - Only companies can post jobs!")
    else:
        print("❌ Should have returned 403 Forbidden")


def test_create_job_success():
    """Test creating job as company (should succeed)"""
    print("\n" + "="*60)
    print("TEST 5: Create Job as COMPANY (Success)")
    print("="*60)
    
    data = {
        "title": "Full Stack Developer",
        "description": "We are looking for a Full Stack Developer with 2-5 years of experience in Python, React, and MongoDB. The candidate will work on building scalable web applications.",
        "company_name": "TCS",
        "location": "Bangalore, India",
        "job_type": "Full-time",
        "experience_required": "2-5 years",
        "salary_min": 800000,
        "salary_max": 1500000,
        "required_skills": ["Python", "React", "MongoDB", "Flask", "JavaScript"],
        "application_deadline": "2024-12-31"
    }
    
    # Use company token
    headers = {"Authorization": f"Bearer {company_token}"}
    response = requests.post(f"{BASE_URL}/jobs/create", json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        global job_id
        job_id = response.json()['job_id']
        print("✅ Job posted successfully!")
        print(f"🆔 Job ID: {job_id}")
        return job_id
    else:
        print("❌ Job creation failed!")
        return None


def test_create_multiple_jobs():
    """Create more jobs for testing"""
    print("\n" + "="*60)
    print("TEST 6: Create Multiple Jobs")
    print("="*60)
    
    jobs = [
        {
            "title": "Backend Developer",
            "description": "Looking for Backend Developer with Node.js experience",
            "company_name": "TCS",
            "location": "Mumbai, India",
            "job_type": "Full-time",
            "experience_required": "1-3 years",
            "salary_min": 600000,
            "salary_max": 1000000,
            "required_skills": ["Node.js", "Express.js", "MongoDB", "REST API"],
            "application_deadline": "2024-11-30"
        },
        {
            "title": "Frontend Developer",
            "description": "Looking for Frontend Developer with React experience",
            "company_name": "TCS",
            "location": "Pune, India",
            "job_type": "Contract",
            "experience_required": "0-2 years",
            "salary_min": 400000,
            "salary_max": 700000,
            "required_skills": ["React", "JavaScript", "CSS", "HTML"],
            "application_deadline": "2024-10-31"
        }
    ]
    
    headers = {"Authorization": f"Bearer {company_token}"}
    
    for i, job_data in enumerate(jobs, 1):
        print(f"\n📝 Creating Job {i}: {job_data['title']}")
        response = requests.post(f"{BASE_URL}/jobs/create", json=job_data, headers=headers)
        
        if response.status_code == 201:
            print(f"   ✅ Created - Job ID: {response.json()['job_id']}")
        else:
            print(f"   ❌ Failed - {response.json()}")


def test_get_all_jobs():
    """Test getting all active jobs (public route)"""
    print("\n" + "="*60)
    print("TEST 7: Get All Jobs (No Auth Required)")
    print("="*60)
    
    # No authentication required for viewing jobs
    response = requests.get(f"{BASE_URL}/jobs/all")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        jobs = response.json()['jobs']
        total = response.json()['total']
        
        print(f"✅ Found {total} active jobs")
        print("\n📋 Jobs List:")
        print("-" * 60)
        
        for job in jobs:
            print(f"\n🔹 {job['job_title']}")
            print(f"   Company: {job['company_name']}")
            print(f"   Location: {job['location']}")
            print(f"   Skills: {', '.join(job['required_skills'])}")
            print(f"   Salary: ₹{job['salary_min']:,} - ₹{job['salary_max']:,}")
            print(f"   Status: {job['status']}")
    else:
        print("❌ Failed to fetch jobs")


def test_get_job_details():
    """Test getting details of specific job"""
    print("\n" + "="*60)
    print("TEST 8: Get Job Details by ID")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Job details fetched successfully!")
    else:
        print("❌ Failed to fetch job details")


def test_filter_jobs():
    """Test filtering jobs by location and skills"""
    print("\n" + "="*60)
    print("TEST 9: Filter Jobs (Location: Bangalore, Skill: Python)")
    print("="*60)
    
    # Filter by location and skills
    params = {
        "location": "Bangalore",
        "skills": "Python"
    }
    
    response = requests.get(f"{BASE_URL}/jobs/all", params=params)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        jobs = response.json()['jobs']
        total = response.json()['total']
        
        print(f"✅ Found {total} jobs matching filters")
        
        for job in jobs:
            print(f"\n🔹 {job['job_title']}")
            print(f"   Location: {job['location']}")
            print(f"   Skills: {', '.join(job['required_skills'])}")
    else:
        print("❌ Failed to filter jobs")


def test_update_job():
    """Test updating a job"""
    print("\n" + "="*60)
    print("TEST 10: Update Job (Increase Salary)")
    print("="*60)
    
    data = {
        "salary_max": 2000000,
        "description": "Updated: We are looking for a Full Stack Developer with expertise in modern web technologies. Excellent growth opportunities!"
    }
    
    headers = {"Authorization": f"Bearer {company_token}"}
    response = requests.put(f"{BASE_URL}/jobs/{job_id}/update", json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Job updated successfully!")
    else:
        print("❌ Failed to update job")


def test_get_my_jobs():
    """Test getting all jobs posted by current company"""
    print("\n" + "="*60)
    print("TEST 11: Get My Posted Jobs (Company Dashboard)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {company_token}"}
    response = requests.get(f"{BASE_URL}/jobs/my-jobs", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        jobs = response.json()['jobs']
        total = response.json()['total']
        
        print(f"✅ You have posted {total} jobs")
        print("\n📋 Your Jobs:")
        print("-" * 60)
        
        for job in jobs:
            print(f"\n🔹 {job['job_title']}")
            print(f"   Applications: {job['applications_count']}")
            print(f"   Status: {job['status']}")
            print(f"   Posted: {job['posted_date']}")
    else:
        print("❌ Failed to fetch your jobs")


def test_close_job():
    """Test closing a job (stop accepting applications)"""
    print("\n" + "="*60)
    print("TEST 12: Close Job (Stop Accepting Applications)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {company_token}"}
    response = requests.put(f"{BASE_URL}/jobs/{job_id}/close", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Job closed successfully!")
    else:
        print("❌ Failed to close job")


def test_delete_job():
    """Test deleting a job"""
    print("\n" + "="*60)
    print("TEST 13: Delete Job (OPTIONAL - Commented Out)")
    print("="*60)
    
    print("⚠️  Job deletion test is commented out to preserve test data")
    print("    Uncomment the code below to test deletion")
    
    # Uncomment to test deletion:
    # headers = {"Authorization": f"Bearer {company_token}"}
    # response = requests.delete(f"{BASE_URL}/jobs/{job_id}/delete", headers=headers)
    # 
    # print(f"Status Code: {response.status_code}")
    # print(f"Response: {json.dumps(response.json(), indent=2)}")
    # 
    # if response.status_code == 200:
    #     print("✅ Job deleted successfully!")
    # else:
    #     print("❌ Failed to delete job")


# ===== RUN ALL TESTS =====

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING JOB POSTING API")
    print("="*60)
    print("Make sure Flask server is running on http://localhost:5000")
    print("="*60)
    
    # Test sequence
    test_register_company()
    test_register_student()
    test_create_job_without_auth()
    test_create_job_as_student()
    test_create_job_success()
    test_create_multiple_jobs()
    test_get_all_jobs()
    test_get_job_details()
    test_filter_jobs()
    test_update_job()
    test_get_my_jobs()
    test_close_job()
    test_delete_job()
    
    # Summary
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print(f"🔑 Company Token: {company_token[:50] if company_token else 'None'}...")
    print(f"🔑 Student Token: {student_token[:50] if student_token else 'None'}...")
    print(f"🆔 Sample Job ID: {job_id if job_id else 'None'}")
    print("="*60)
    print("\n📌 Next Steps:")
    print("   1. Check MongoDB Atlas - 'jobs' collection created")
    print("   2. Try filtering jobs with different parameters")
    print("   3. Ready for Step 7: Job-Resume Matching Algorithm!")
    print("="*60 + "\n")
