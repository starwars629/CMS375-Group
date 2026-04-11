"""
Authentication and Authroization Utilities
==========================================
This module provides decorators and helper functions for:
- JWT token creation and validation
- Password hashing and verification
- Route protection (authentication)
- Role-based access control
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
from utils.validators import validate_password_strength, validate_email

# =====================================
# Configuration
# =====================================

# THIS SHOULD BE STORED IN AN ENVIRONMENTAL VARIABLE FOLLOWING PRODUCTION
SECRET_KEY = 'this-is-a-very-secure-key-that-is-at-least-32-bytes-long'

# Token expiration time
TOKEN_EXPIRATION_HOURS = 24

# Valid user roles
VALID_ROLES = ['student', 'faculty', 'librarian', 'admin']

# =====================================
# Password Hashing
# =====================================

def hash_password(password):
    """
        hash a password using bcrypt

        args:
            password (str): plain text password

        returns:
            str: hashed password
    """

    # Convert to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify a password against its hash

    args:
        password (str): plain text password to check
        hashed_password: hashed password from database

    returns:
        bool: passwords match
    """

    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)

# =====================================
# JWT Token Functions
# =====================================

def create_token(user_id, role, name=None, email=None):
    """
    Creates a JWT authentication token
    
    args:
        user_id (int): User's ID from database
        role (str): User's roles (student, faculty, librarian, admin)
        name (str, optional): User's name
        email (str, optional): User's email

    returns: 
        str: JWT token
    """

    # Calculate expiration time
    expiration = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS)

    # Create payload
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': expiration,
        'iat': datetime.utcnow() # Issued at
    }

    # Add optional fields
    if name :
        payload['name'] = name
    if email:
        payload['email'] = email

    # Encode and return token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token 

def decode_token(token):
    """
    Decode and validate a JWT Token
    
    args: 
        token (str): JWT token to decode

    returns:
        dict: decoded payload token, or None if invalid

    raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Token has expired')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token')

# =====================================
# Authentication Decorators
# =====================================

def require_auth(f):
    """
    Decorator to require authentication for a route

    Checks for valid JWT token in Authentication header
    If valid will add users info to request.current_user

    usage:
        @app.route('/api/protected')
        @require_auth
        def protected_route():
            user_id = request.currest_user['user_id']
            return {'message': f'Hello user {user_id}'}

    headers required:
        Authorization: Bearer <token>
        
    returns:
        401: If no token provided
        401: If token is invalid or expired
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'No authentication token provided'}), 401
        
        try:
            # Extract token (format: "Bearer <token>")
            parts = auth_header.split()

            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'error': 'Invalid authentication header format. Use "Bearer <token>"'}), 401
            
            token = parts[1]

            # Decode token
            payload = decode_token(token)

            # Add user info to request object
            request.current_user = payload

            # Call the actual route function
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired. Please login again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token. Please login again'}), 401
        except Exception as e:
            print(f'Authentication error {e}')
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

def require_role(*allowed_roles):
    """
    Decorator to require specific role(s) for a route
    Must be used AFTER @require_auth

    args:
        *allowed_roles: One or more role names (student, faculty, librarian, admin)

    usage:
        @app.route('/api/books/', methods=['POST'])
        @require_auth
        @require_role('librarian', 'admin')
        def addbooks():
            return {'message': 'Book added'}

    returns:
        403: If user doesn't have the required role
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication error'}), 401
            
            # Get a user's role
            user_role = request.current_user.get('role')

            # Check if user has one of the allowed roles
            if user_role not in allowed_roles:
                roles_str = ' or '.join(allowed_roles)
                return jsonify({'error': f'Access denied. Required roles: {roles_str}', 
                                'your_role': user_role}), 403
            
            # User has required role (proceed)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def optional_auth(f):
    """
    Decorator for optional authentication
    If token is provided, validate it and add to the request
    else, continue without authentication

    Useful for endpoints that behave differently for authenticated users

    Usage:
        @app.route('/api/books')
        @optional_auth
        def get_books():
            user = get_current_user()
            if user:
                # Show personalized recommendations
                pass
            else:
                # Show general catalog
                pass
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if auth_header:
            try:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    token = parts[1]
                    payload = decode_token(token)
                    request.current_user = payload
            except:
                # Invalid token - continue
                pass
        return f(*args, **kwargs)
    return decorated_function

# =====================================
# Helper Functionrs
# =====================================

def get_current_user():
    """
    Get current authenticated user information

    returns:
        If no user authenticated:
            None
        else:
            dict: current user's information from token

    usage:
        @app.route('/api/profile')
        @require_auth
        def get_profile():
            user = get_current_user()
            return {'user_id': user['user_id'], 'role': user['role']}
    """

    if hasattr(request, 'current_user'):
        return request.current_user
    return None

def get_current_user_id():
    """
    Get current authenticated user's ID

    returns:
        If no user authenticated:
            None
        else:
            int: Current user's ID
    """

    user = get_current_user()
    return user['user_id'] if user else None

def get_current_user_role():
    """
    Get current authenticated user's role

    returns:
        If no user authenticated:
            None
        else: 
            str: Current user's role (student, faculty, librarian, admin)
    """

    user = get_current_user()
    return user['role'] if user else None

# ============================================
# Debug/Testing Functions
# ============================================

def create_test_token(user_id=1, role='student'):
    """
    Create a test token for development/testing.
    
    WARNING: Only use in development!
    
    Args:
        user_id (int): Test user ID
        role (str): Test user role
    
    Returns:
        str: JWT token
    """
    return create_token(
        user_id=user_id,
        role=role,
        name='Test User',
        email='test@example.com'
    )


if __name__ == '__main__':
    """
    Test the authentication utilities
    """
    print("=" * 50)
    print("Testing Authentication Utilities")
    print("=" * 50)
    
    # Test password hashing
    print("\n1. Testing Password Hashing:")
    password = "mySecurePassword123"
    hashed = hash_password(password)
    print(f"   Original: {password}")
    print(f"   Hashed: {hashed}")
    print(f"   Verification: {verify_password(password, hashed)}")
    print(f"   Wrong password: {verify_password('wrongpassword', hashed)}")
    
    # Test token creation
    print("\n2. Testing Token Creation:")
    token = create_token(user_id=42, role='student', name='John Doe', email='john@example.com')
    print(f"   Token: {token[:50]}...")
    
    # Test token decoding
    print("\n3. Testing Token Decoding:")
    payload = decode_token(token)
    print(f"   User ID: {payload['user_id']}")
    print(f"   Role: {payload['role']}")
    print(f"   Name: {payload.get('name')}")
    print(f"   Email: {payload.get('email')}")
    print(f"   Expires: {datetime.fromtimestamp(payload['exp'])}")
    
    # Test password validation
    print("\n4. Testing Password Validation:")
    weak_passwords = ["abc", "12345678", "abcdefgh"]
    strong_password = "SecurePass123"
    
    for pwd in weak_passwords:
        valid, msg = validate_password_strength(pwd)
        print(f"   '{pwd}': {valid} - {msg}")
    
    valid, msg = validate_password_strength(strong_password)
    print(f"   '{strong_password}': {valid}")
    
    # Test email validation
    print("\n5. Testing Email Validation:")
    emails = ["user@example.com", "invalid-email", "test@test", "valid.email@domain.co.uk"]
    for email in emails:
        print(f"   '{email}': {validate_email(email)}")
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)