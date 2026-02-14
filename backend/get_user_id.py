# get_user_id.py - Simple script to get your user ID for testing
import requests
import json

BASE_URL = "http://localhost:5000/api/auth"

print("="*60)
print("🔑 GET YOUR USER ID FOR RESUME UPLOAD TESTING")
print("="*60)

# Login to get user info
data = {
    "email": "john@student.com",
    "password": "Student@123"
}

print("\n📡 Logging in as John (Student)...")
response = requests.post(f"{BASE_URL}/login", json=data)

if response.status_code == 200:
    result = response.json()
    user_id = result['user']['id']  # Note: 'id' not '_id'
    token = result['token']
    
    print("\n✅ Login Successful!")
    print("\n" + "="*60)
    print("📋 YOUR USER ID:")
    print("="*60)
    print(f"\n   {user_id}")
    print("\n" + "="*60)
    print("\n💡 COPY THIS USER ID - You'll need it for resume upload!")
    print("\n📝 Token (for headers):")
    print(f"   {token}")
    print("\n" + "="*60)
else:
    print("\n❌ Login failed! Make sure the Flask server is running.")
    print(f"Error: {response.json()}")
