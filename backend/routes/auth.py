from flask import Blueprint, request, jsonify
from utils.database import execute_query
from utils.auth import (
    hash_password,
    verify_password,
    create_token,
    validate_password_strength,
    validate_email,
    require_auth,
    get_current_user

)
from utils.validators import sanitize_text

bp = Blueprint('auth', __name__, url_prefix='/api/auth')
@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user

    POST /api/auth/register {
    "name": "John Doe",
    "email": "John@example.com",
    "password": "SecurePass123"
    }
    """

    data = request.json

    # Validate required information
    errors = ''
    if not data.get('email'):
        errors += '| Email is required'
    if not data.get('password'):
        errors += '| Password is required'
    if not data.get('name'):
        errors += '| Name is required'
    
    if len(errors) != 0:
        return jsonify({'error': errors}), 400
    
    sanitized_name = sanitize_text(data['name'], max_length=100)
    sanitized_email = sanitize_text(data['email'], max_length=150).lower()

    # Validate strength and uniqueness
    if not validate_email(sanitized_email):
        return jsonify({'error': 'Invalid email format'}), 400

    valid, error_msg = validate_password_strength(data['password'])
    if not valid:
        return jsonify({'error': error_msg}), 400

    existing = execute_query(
        'SELECT user_id FROM Users WHERE email = %s',
        (sanitized_email,),
        fetch_one=True
    )
    if existing:
        return jsonify({'error': 'Email already registered'}), 409
    
    # Hash password
    hashed_password = hash_password(data['password'])

    # Create user
    try:
        user_id = execute_query("""
            INSERT INTO Users (name, email, password, role, fine_balance)
            VALUES (%s, %s, %s, 'student', 0.00)
            """, (sanitized_name, sanitized_email, hashed_password))
        
        return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
    except Exception as e:
        print(f'Registration error: {e}')
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """
    Login user and receive token
    
    POST /api/auth/login {
        "email": "john@example.com",
        "password": "SecurePass123"
    }
    """

    data = request.json

    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    sanitized_email = sanitize_text(data['email'], max_length=150).lower()

    # Get user from database
    user = execute_query(
        "SELECT * FROM Users WHERE email = %s",
        (sanitized_email,),
        fetch_one=True
    )

    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Verify password
    if not verify_password(data['password'], user['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create token
    token = create_token(
        user_id=user['user_id'],
        role=user['role'],
        name=user['name'],
        email=user['email']
    )
    
    # Remove password from response
    del user['password']
    
    return jsonify({
        'token': token,
        'user': user
    }), 200

@bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout user
    (Client-side delete token)
    """

    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """
    Change user password
    
    POST /api/auth/change-password {
        "current_password": "oldPass123",
        "new_password": "newSecurePass456"
    }
    """
    data = request.json
    user = get_current_user()
    
    # Validate required fields
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password required'}), 400
    
    # Validate new password strength
    valid, error_msg = validate_password_strength(data['new_password'])
    if not valid:
        return jsonify({'error': error_msg}), 400
    
    # Get user's current password hash
    user_data = execute_query(
        "SELECT password FROM Users WHERE user_id = %s",
        (user['user_id'],),
        fetch_one=True
    )

    # Verify current password
    if not verify_password(data['current_password'], user_data['password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Hash new password
    new_hashed = hash_password(data['new_password'])
    
    # Update password
    execute_query(
        "UPDATE Users SET password = %s WHERE user_id = %s",
        (new_hashed, user['user_id'])
    )
    
    return jsonify({'message': 'Password changed successfully'}), 200