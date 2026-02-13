# test_auth.py - Test authentication endpoints
# This file demonstrates how to test registration and login

import requests
import json

# Base URL of the API
BASE_URL = "http://localhost:5000/api/auth"

def test_register_student():
    """Test student registration"""
    print("\n" + "="*50)
    print("TEST 1: Register Student")
    print("="*50)
    
    # Student registration data
    data = {
        "name": "John Doe",
        "email": "john@student.com",
        "password": "Student@123",
        "role": "student",
        "phone": "+919876543210"
    }
    
    # Send POST request
    response = requests.post(f"{BASE_URL}/register", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Student registered successfully!")
        return response.json()['token']
    else:
        print("❌ Registration failed!")
        return None


def test_register_company():
    """Test company registration"""
    print("\n" + "="*50)
    print("TEST 2: Register Company")
    print("="*50)
    
    # Company registration data
    data = {
        "name": "Google Recruiter",
        "email": "recruiter@google.com",
        "password": "Company@123",
        "role": "company",
        "phone": "+919876543211"
    }
    
    # Send POST request
    response = requests.post(f"{BASE_URL}/register", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Company registered successfully!")
        return response.json()['token']
    else:
        print("❌ Registration failed!")
        return None


def test_login():
    """Test user login"""
    print("\n" + "="*50)
    print("TEST 3: Login")
    print("="*50)
    
    # Login credentials
    data = {
        "email": "john@student.com",
        "password": "Student@123"
    }
    
    # Send POST request
    response = requests.post(f"{BASE_URL}/login", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        return response.json()['token']
    else:
        print("❌ Login failed!")
        return None


def test_get_profile(token):
    """Test getting user profile with token"""
    print("\n" + "="*50)
    print("TEST 4: Get Profile (Protected Route)")
    print("="*50)
    
    # Add token to headers
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Send GET request
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Profile retrieved successfully!")
    else:
        print("❌ Failed to get profile!")


def test_invalid_login():
    """Test login with wrong password"""
    print("\n" + "="*50)
    print("TEST 5: Invalid Login")
    print("="*50)
    
    data = {
        "email": "john@student.com",
        "password": "WrongPassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✅ Correctly rejected invalid password!")
    else:
        print("❌ Security issue - accepted wrong password!")


def test_weak_password():
    """Test registration with weak password"""
    print("\n" + "="*50)
    print("TEST 6: Weak Password Validation")
    print("="*50)
    
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "weak",  # Too weak!
        "role": "student"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 400:
        print("✅ Correctly rejected weak password!")
    else:
        print("❌ Validation issue - accepted weak password!")


# Run all tests
if __name__ == "__main__":
    print("\n🧪 AUTHENTICATION API TESTS")
    print("="*50)
    print("Make sure Flask server is running on http://localhost:5000")
    print("="*50)
    
    try:
        # Test student registration
        student_token = test_register_student()
        
        # Test company registration
        company_token = test_register_company()
        
        # Test login
        login_token = test_login()
        
        # Test protected route
        if login_token:
            test_get_profile(login_token)
        
        # Test invalid login
        test_invalid_login()
        
        # Test weak password
        test_weak_password()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS COMPLETED!")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure Flask server is running: python backend/app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
