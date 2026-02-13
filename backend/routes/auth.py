# auth.py - Authentication routes (register, login, profile)
# This file handles user registration, login, and authentication

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from bson import ObjectId

from models.user import User
from utils.validators import validate_registration_data, is_valid_email, sanitize_input
from config import Config

# Create a Blueprint for authentication routes
# Blueprint is like a mini-application that can be registered with the main app
auth_bp = Blueprint('auth', __name__)

# Import database from app (will be injected later)
db = None

def init_auth_routes(database):
    """
    Initialize auth routes with database connection
    
    Args:
        database: MongoDB database instance
    """
    global db
    db = database


# ===== HELPER FUNCTIONS =====

def create_jwt_token(user_id, email, role):
    """
    Create JWT token for authenticated user
    
    Args:
        user_id (str): User's MongoDB ID
        email (str): User's email
        role (str): User's role (student/company/admin)
        
    Returns:
        str: JWT token string
        
    Example:
        Token contains: user_id, email, role, expiry time
        Like a movie ticket with seat number and show time
    """
    # Create payload (data to encode in token)
    payload = {
        'user_id': str(user_id),  # Convert ObjectId to string
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES,  # Expiry time
        'iat': datetime.utcnow()  # Issued at time
    }
    
    # Encode payload into JWT token
    # Like sealing information in an encrypted envelope
    token = jwt.encode(
        payload,
        Config.SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )
    
    return token


def token_required(f):
    """
    Decorator to protect routes (require valid JWT token)
    
    Usage:
        @auth_bp.route('/protected')
        @token_required
        def protected_route(current_user):
            # Only accessible with valid token
            return "Welcome " + current_user['name']
    
    How it works:
    1. User sends request with token in header
    2. This function checks if token is valid
    3. If valid, allows access + provides user data
    4. If invalid, returns error
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from request header
        # Format: Authorization: Bearer <token>
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # Split "Bearer token123" → get "token123"
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        # If no token provided
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode the token
            # Like opening the encrypted envelope
            data = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=[Config.JWT_ALGORITHM]
            )
            
            # Get user from database
            current_user = db['users'].find_one({'_id': ObjectId(data['user_id'])})
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            # Remove password from user data (security)
            current_user.pop('password', None)
            
        except jwt.ExpiredSignatureError:
            # Token has expired (after 24 hours)
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            # Token is invalid or tampered
            return jsonify({'error': 'Token is invalid'}), 401
        
        # Pass current_user to the protected route
        return f(current_user, *args, **kwargs)
    
    return decorated


def role_required(allowed_roles):
    """
    Decorator to restrict routes by role
    
    Usage:
        @auth_bp.route('/admin-only')
        @token_required
        @role_required(['admin'])
        def admin_route(current_user):
            # Only admins can access
            return "Admin panel"
    
    Args:
        allowed_roles (list): List of roles that can access
    """
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            # Check if user's role is in allowed_roles
            if current_user['role'] not in allowed_roles:
                return jsonify({
                    'error': 'Access denied',
                    'message': f'This route is only for {", ".join(allowed_roles)}'
                }), 403
            
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator


# ===== AUTHENTICATION ROUTES =====

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user (student, company, or admin)
    
    Request Body (JSON):
        {
            "name": "John Doe",
            "email": "john@gmail.com",
            "password": "Pass@123",
            "role": "student",  // or "company" or "admin"
            "phone": "+919876543210"  // optional
        }
    
    Returns:
        JSON: Success message or error
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate registration data
        is_valid, error_message = validate_registration_data(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Check if email already exists
        existing_user = db['users'].find_one({'email': data['email'].lower()})
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Sanitize input
        name = sanitize_input(data['name'])
        email = data['email'].lower().strip()
        password = data['password']
        role = data['role'].lower()
        phone = data.get('phone', None)
        
        # Hash the password
        # NEVER store plain password!
        # "Pass@123" becomes "$2b$12$xyz..." (irreversible)
        hashed_password = generate_password_hash(
            password,
            method='pbkdf2:sha256'
        )
        
        # Create User object
        user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role,
            phone=phone
        )
        
        # Convert to dictionary for MongoDB
        user_dict = user.to_dict()
        
        # Insert into database
        result = db['users'].insert_one(user_dict)
        user_id = result.inserted_id
        
        # Create JWT token
        token = create_jwt_token(user_id, email, role)
        
        # Return success response
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': str(user_id),
                'name': name,
                'email': email,
                'role': role
            },
            'token': token
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    
    Request Body (JSON):
        {
            "email": "john@gmail.com",
            "password": "Pass@123"
        }
    
    Returns:
        JSON: User data and JWT token
    """
    try:
        # Get credentials from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Find user in database
        user = db['users'].find_one({'email': email})
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check password
        # compare: hashed password in DB vs plain password from user
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create JWT token
        token = create_jwt_token(user['_id'], user['email'], user['role'])
        
        # Return user data (without password!)
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'phone': user.get('phone'),
                'created_at': user['created_at'].isoformat() if user.get('created_at') else None
            },
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Get current user's profile
    
    Protected route - requires valid JWT token
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        JSON: User profile data
    """
    try:
        return jsonify({
            'user': {
                'id': str(current_user['_id']),
                'name': current_user['name'],
                'email': current_user['email'],
                'role': current_user['role'],
                'phone': current_user.get('phone'),
                'student_profile': current_user.get('student_profile'),
                'company_profile': current_user.get('company_profile'),
                'created_at': current_user['created_at'].isoformat() if current_user.get('created_at') else None
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Update current user's profile
    
    Protected route - requires valid JWT token
    
    Request Body (JSON):
        For students:
        {
            "name": "Updated Name",
            "phone": "+919876543210",
            "student_profile": {
                "education": "B.Tech CS",
                "experience_years": 2,
                "location": "Mumbai",
                "bio": "Passionate developer"
            }
        }
        
        For companies:
        {
            "name": "Updated Name",
            "company_profile": {
                "company_name": "Google Inc",
                "industry": "Technology",
                "website": "https://google.com"
            }
        }
    
    Returns:
        JSON: Updated user data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Fields that can be updated
        update_fields = {}
        
        if 'name' in data:
            update_fields['name'] = sanitize_input(data['name'])
        
        if 'phone' in data:
            update_fields['phone'] = data['phone']
        
        # Role-specific updates
        if current_user['role'] == 'student' and 'student_profile' in data:
            update_fields['student_profile'] = data['student_profile']
        
        if current_user['role'] == 'company' and 'company_profile' in data:
            update_fields['company_profile'] = data['company_profile']
        
        # Update in database
        db['users'].update_one(
            {'_id': current_user['_id']},
            {'$set': update_fields}
        )
        
        # Get updated user
        updated_user = db['users'].find_one({'_id': current_user['_id']})
        updated_user.pop('password', None)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': str(updated_user['_id']),
                'name': updated_user['name'],
                'email': updated_user['email'],
                'role': updated_user['role'],
                'phone': updated_user.get('phone'),
                'student_profile': updated_user.get('student_profile'),
                'company_profile': updated_user.get('company_profile')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500
