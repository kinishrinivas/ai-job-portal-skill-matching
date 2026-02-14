# test_skill_extraction.py - Test skill extraction without file upload
# This demonstrates how the AI skill extraction works

from utils.skill_extractor import skill_extractor

def test_skill_extraction():
    """Test skill extraction from resume text"""
    print("\n" + "="*60)
    print("🧪 AI SKILL EXTRACTION TEST")
    print("="*60)
    
    # Sample resume text
    resume_text = """
JOHN DOE
Email: john.doe@email.com
Phone: +91-9876543210

SUMMARY
Full-Stack Developer with 5 years of experience building scalable web applications.
Proficient in Python, JavaScript, React, and MongoDB.

EDUCATION
B.Tech in Computer Science, MIT, 2019

TECHNICAL SKILLS
Programming: Python, JavaScript, Java, C++, TypeScript
Frontend: React, Angular, Vue.js, HTML, CSS, Bootstrap
Backend: Flask, Django, Node.js, Express.js
Databases: MongoDB, MySQL, PostgreSQL, Redis
Cloud: AWS, Docker, Kubernetes, Git

EXPERIENCE
Senior Developer at Tech Corp (2021-Present)
- Built REST APIs using Python Flask and Node.js
- Developed frontend applications with React and TypeScript
- Managed databases including MongoDB and PostgreSQL
- Deployed applications on AWS using Docker containers
- Implemented CI/CD pipelines with Jenkins

Junior Developer at StartUp Inc (2019-2021)
- Created web applications using Django and React
- Worked with MySQL databases
- Used Git for version control
"""
    
    print("\n📄 SAMPLE RESUME TEXT:")
    print("-" * 60)
    print(resume_text[:300] + "...")
    
    # Extract skills
    print("\n🤖 EXTRACTING SKILLS...")
    skills = skill_extractor.extract_skills(resume_text)
    
    print(f"\n✅ FOUND {len(skills)} SKILLS:")
    print("-" * 60)
    for i, skill in enumerate(skills, 1):
        print(f"{i:2d}. {skill}")
    
    # Extract other information
    print("\n📧 EXTRACTING CONTACT INFO...")
    email = skill_extractor.extract_email(resume_text)
    phone = skill_extractor.extract_phone(resume_text)
    
    print(f"   Email: {email}")
    print(f"   Phone: {phone}")
    
    # Extract education
    print("\n🎓 EXTRACTING EDUCATION...")
    education = skill_extractor.extract_education(resume_text)
    print(f"   Education: {education}")
    
    # Extract experience
    print("\n💼 EXTRACTING EXPERIENCE...")
    experience_years = skill_extractor.extract_experience_years(resume_text)
    print(f"   Years of Experience: {experience_years}")
    
    # Calculate confidence
    confidence = skill_extractor.calculate_confidence(skills, len(resume_text))
    print(f"\n📊 CONFIDENCE SCORE: {confidence:.2f}%")
    
    print("\n" + "="*60)
    print("✅ SKILL EXTRACTION TEST COMPLETED!")
    print("="*60)
    
    return skills


def test_with_different_resumes():
    """Test skill extraction with different resume formats"""
    print("\n" + "="*60)
    print("🧪 TESTING DIFFERENT RESUME FORMATS")
    print("="*60)
    
    test_cases = [
        {
            "name": "Experienced in Python",
            "text": "I have 3 years experience in Python and JavaScript. Also worked with React.",
            "expected": ["Python", "JavaScript", "React"]
        },
        {
            "name": "Proficient in",
            "text": "Proficient in Flask, Django, and MongoDB. Knowledge of AWS and Docker.",
            "expected": ["Flask", "Django", "MongoDB", "AWS", "Docker"]
        },
        {
            "name": "Skills list",
            "text": "Technical Skills: C++, Java, Python, MySQL, Git, REST API",
            "expected": ["C++", "Java", "Python", "MySQL", "Git", "REST API"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"   Text: \"{test_case['text']}\"")
        
        skills = skill_extractor.extract_skills(test_case['text'])
        print(f"   Found: {skills}")
        print(f"   Expected: {test_case['expected']}")
        
        # Check if all expected skills were found
        found_all = all(skill in skills for skill in test_case['expected'])
        status = "✅ PASS" if found_all else "⚠️  PARTIAL"
        print(f"   Status: {status}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 AI SKILL EXTRACTION DEMONSTRATION")
    print("="*60)
    print("\nThis test demonstrates how our AI extracts skills from resumes")
    print("without uploading actual files.\n")
    
    # Test main skill extraction
    test_skill_extraction()
    
    # Test different formats
    test_with_different_resumes()
    
    print("\n" + "="*60)
    print("💡 HOW IT WORKS:")
    print("="*60)
    print("""
1. Text Extraction: Read text from PDF/DOCX files
2. Pattern Matching: Find keywords matching our skills database  
3. Context Analysis: Look for phrases like "proficient in", "experience with"
4. Validation: Match against 100+ known skills in our database
5. Confidence Calculation: Score based on text length and skills found

Our system matches skills like:
- Programming languages: Python, JavaScript, Java, C++
- Frameworks: React, Flask, Django, Node.js
- Databases: MongoDB, MySQL, PostgreSQL
- Cloud & DevOps: AWS, Docker, Kubernetes, Git
- And many more!
""")
    
    print("="*60)
    print("🎯 NEXT STEPS:")
    print("="*60)
    print("""
To test with actual resume files:
1. Create a PDF resume using Word/Google Docs
2. Save it as resume.pdf
3. Use Postman or curl to upload:
   
   curl -X POST http://localhost:5000/api/resume/upload \\
     -F "resume=@resume.pdf" \\
     -F "user_id=YOUR_USER_ID"

Or wait for the frontend where you can upload via web interface!
""")
