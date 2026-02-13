# validators.py - Input validation functions
# This file checks if user input is valid before processing

import re
from bson import ObjectId

def is_valid_email(email):
    """
    Check if email format is valid
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Example:
        is_valid_email("john@gmail.com") → True
        is_valid_email("notanemail") → False
    """
    # Regular expression pattern for email validation
    # Explanation: text@text.text format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # re.match() checks if string matches the pattern
    return re.match(email_pattern, email) is not None


def is_strong_password(password):
    """
    Check if password is strong enough
    
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
        
    Example:
        is_strong_password("Pass@123") → (True, "")
        is_strong_password("weak") → (False, "Password must be at least 8 characters")
    """
    # Check length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase letter
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    # All checks passed
    return True, ""


def is_valid_role(role):
    """
    Check if user role is valid
    
    Args:
        role (str): User role
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Only these 3 roles are allowed
    valid_roles = ['student', 'company', 'admin']
    return role in valid_roles


def is_valid_phone(phone):
    """
    Check if phone number format is valid
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Example:
        is_valid_phone("+919876543210") → True
        is_valid_phone("12345") → False
    """
    # Remove spaces and dashes
    phone = phone.replace(' ', '').replace('-', '')
    
    # Check if it's 10-15 digits (with optional + at start)
    phone_pattern = r'^\+?[0-9]{10,15}$'
    return re.match(phone_pattern, phone) is not None


def is_valid_objectid(id_string):
    """
    Check if string is a valid MongoDB ObjectId
    
    Args:
        id_string (str): ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        ObjectId(id_string)
        return True
    except:
        return False


def sanitize_input(text):
    """
    Remove dangerous characters from input
    Prevents XSS (Cross-Site Scripting) attacks
    
    Args:
        text (str): Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
    
    # Trim whitespace
    text = text.strip()
    
    return text


def validate_registration_data(data):
    """
    Validate all registration data
    
    Args:
        data (dict): Registration form data
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['name', 'email', 'password', 'role']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    # Validate email
    if not is_valid_email(data['email']):
        return False, "Invalid email format"
    
    # Validate password
    is_valid, error = is_strong_password(data['password'])
    if not is_valid:
        return False, error
    
    # Validate role
    if not is_valid_role(data['role']):
        return False, "Invalid role. Must be 'student', 'company', or 'admin'"
    
    # Validate phone if provided
    if 'phone' in data and data['phone']:
        if not is_valid_phone(data['phone']):
            return False, "Invalid phone number format"
    
    # All validations passed
    return True, ""
