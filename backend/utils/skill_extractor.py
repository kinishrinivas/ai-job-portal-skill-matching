# skill_extractor.py - AI/NLP for extracting skills from resume text
# This file finds skills mentioned in resume text

import re
from config import Config

class SkillExtractor:
    """
    Extract skills from resume text
    
    Uses pattern matching against a known skills database
    In a production app, this would use NLP libraries like spaCy or transformers
    """
    
    def __init__(self):
        """Initialize with known skills database"""
        # Load known skills from config
        self.known_skills = set(skill.lower() for skill in Config.KNOWN_SKILLS)
        
        # Common skill variations (different ways to write same skill)
        self.skill_variations = {
            'javascript': ['js', 'javascript', 'java script', 'ecmascript'],
            'node.js': ['nodejs', 'node.js', 'node js', 'expressjs', 'express.js'],
            'react': ['react', 'reactjs', 'react.js', 'react native'],
            'python': ['python', 'python3', 'python 3'],
            'sql': ['sql', 'mysql', 'postgresql', 'sqlite', 'tsql', 't-sql'],
            'html/css': ['html', 'css', 'html5', 'css3', 'scss', 'sass'],
            'c++': ['c++', 'cpp', 'c plus plus'],
            'c#': ['c#', 'csharp', 'c sharp'],
        }
    
    def extract_skills(self, text):
        """
        Extract skills from text
        
        Args:
            text (str): Resume text to analyze
            
        Returns:
            list: List of unique skills found
            
        Example:
            text = "I have 3 years experience in Python, React, and MongoDB"
            extract_skills(text) → ["Python", "React", "MongoDB"]
        """
        if not text:
            return []
        
        # Convert to lowercase for matching
        text_lower = text.lower()
        
        # Found skills (use set to avoid duplicates)
        found_skills = set()
        
        # Method 1: Direct word matching
        # Split text into words and check against known skills
        words = re.findall(r'\b[\w\+\#\.]+\b', text_lower)
        # \b = word boundary, \w = word character, \+ = literal +, \# = literal #
        
        for word in words:
            if word in self.known_skills:
                # Find the original case from Config.KNOWN_SKILLS
                original_skill = self._find_original_case(word)
                found_skills.add(original_skill)
        
        # Method 2: Multi-word skills (e.g., "Machine Learning", "REST API")
        for skill in Config.KNOWN_SKILLS:
            if len(skill.split()) > 1:  # Multi-word skill
                # Check if skill appears in text (case-insensitive)
                if skill.lower() in text_lower:
                    found_skills.add(skill)
        
        # Method 3: Check skill variations
        for standard_skill, variations in self.skill_variations.items():
            for variation in variations:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(variation) + r'\b'
                if re.search(pattern, text_lower):
                    # Add the standard skill name
                    original_skill = self._find_original_case(standard_skill)
                    if original_skill:
                        found_skills.add(original_skill)
                    break  # Found this skill, no need to check other variations
        
        # Method 4: Context-based extraction (look for common patterns)
        # Pattern: "proficient in X", "experience with X", "knowledge of X"
        context_patterns = [
            r'proficient in ([a-z\+\#\. ]+)',
            r'experience (?:with|in) ([a-z\+\#\. ]+)',
            r'knowledge of ([a-z\+\#\. ]+)',
            r'skilled in ([a-z\+\#\. ]+)',
            r'expertise in ([a-z\+\#\. ]+)',
            r'working with ([a-z\+\#\. ]+)',
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Split by comma or 'and'
                potential_skills = re.split(r',|\sand\s', match)
                for skill_text in potential_skills:
                    skill_text = skill_text.strip()
                    if skill_text in self.known_skills:
                        original_skill = self._find_original_case(skill_text)
                        found_skills.add(original_skill)
        
        # Convert set to sorted list
        return sorted(list(found_skills))
    
    def _find_original_case(self, skill_lower):
        """
        Find the original case of a skill from Config.KNOWN_SKILLS
        
        Args:
            skill_lower (str): Lowercase skill name
            
        Returns:
            str: Original case skill name or None
        """
        for skill in Config.KNOWN_SKILLS:
            if skill.lower() == skill_lower:
                return skill
        return None
    
    def extract_email(self, text):
        """
        Extract email address from text
        
        Args:
            text (str): Resume text
            
        Returns:
            str: Email address or None
        """
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        
        # Return first email found
        return matches[0] if matches else None
    
    def extract_phone(self, text):
        """
        Extract phone number from text
        
        Args:
            text (str): Resume text
            
        Returns:
            str: Phone number or None
        """
        # Phone patterns (various formats)
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 (123) 456-7890
            r'\b\d{10}\b',  # 1234567890
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 123-456-7890
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return None
    
    def extract_education(self, text):
        """
        Extract education information from text
        
        Args:
            text (str): Resume text
            
        Returns:
            str: Education details or None
        """
        # Common degree patterns
        degree_patterns = [
            r'\b(B\.?Tech|Bachelor of Technology|BE|B\.E\.|Bachelor of Engineering)\b',
            r'\b(M\.?Tech|Master of Technology|ME|M\.E\.|Master of Engineering)\b',
            r'\b(MBA|Master of Business Administration)\b',
            r'\b(B\.?Sc|Bachelor of Science|M\.?Sc|Master of Science)\b',
            r'\b(BCA|Bachelor of Computer Applications|MCA|Master of Computer Applications)\b',
            r'\b(PhD|Ph\.D\.|Doctorate)\b',
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Try to get surrounding context (university, year, etc.)
                # For simplicity, just return the degree
                return matches[0]
        
        return None
    
    def extract_experience_years(self, text):
        """
        Estimate years of experience from text
        
        Args:
            text (str): Resume text
            
        Returns:
            int: Estimated years of experience
        """
        # Patterns like "5 years experience", "3+ years", "2-4 years"
        experience_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+(?:in|with)',
            r'experience[:\s]+(\d+)\+?\s*years?',
        ]
        
        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    years.append(int(match))
                except:
                    pass
        
        # Return maximum years found (conservative estimate)
        return max(years) if years else 0
    
    def calculate_confidence(self, skills_found, text_length):
        """
        Calculate confidence score for extraction
        
        Args:
            skills_found (list): List of skills extracted
            text_length (int): Length of resume text
            
        Returns:
            float: Confidence score (0-100)
        """
        # Basic heuristic:
        # - More skills found = higher confidence
        # - Longer text = higher confidence (more data to analyze)
        # - But cap at 95% (never 100% confident in automated extraction)
        
        skill_score = min(len(skills_found) * 5, 50)  # Up to 50 points
        length_score = min(text_length / 100, 40)     # Up to 40 points
        base_score = 5  # Minimum 5 points
        
        confidence = base_score + skill_score + length_score
        return min(confidence, 95.0)  # Cap at 95%


# Create a singleton instance
skill_extractor = SkillExtractor()
