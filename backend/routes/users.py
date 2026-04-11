from flask import Blueprint, request, jsonify
from utils.auth import (
    require_auth, 
    require_role,
    get_current_user,
    get_current_user_id,
    get_current_user_role,
    validate_email
)
from utils.database import execute_query

bp = Blueprint('users', __name__, url_prefix='/api/users')


# =======================
# GET /api/users/me - Get Current User Profile
# =======================

@bp.route('/me', methods=['GET'])
@require_auth
def get_my_profile():
    """
    Get current user's profile
    
    GET /api/users/me
    Headers: Authorization: Bearer <token>

    Returns:
        200: User profile with stats
    """

    user_id = get_current_user_id()

    user = execute_query(
        "SELECT user_id, name, email, role, fine_balance, created_at FROM Users WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    stats = execute_query("""
        SELECT 
            COUNT(CASE WHEN status IN ('active', 'overdue') THEN 1 END) AS currently_borrowed
            COUNT(CASE WHEN status = 'overdue' THEN 1 END) AS overdue_books
            COUNT(*) as total_books_borrowed
        FROM Loans
        WHERE user_id = %s
    """, (user_id,), fetch_one=True)

    reservations = execute_query("""
        SELECT COUNT(*) as pending_reservations
        FROM Reservations
        WHERE user_id = %s AND status = 'pending'
    """, (user_id,), fetch_one=True)

    user['stats'] = {
        'total_books_borrowed': stats['total_books_borrowed'] if stats else 0,
        'currently_borrowed': stats['currently_borrowed'] if stats else 0,
        'overdue_books': stats['overdue_books'] if stats else 0,
        'pending_reservations': reservations['pending_reservations'] if reservations else 0
    }

    return jsonify(user), 200

# =======================
# GET /api/users/{user_id} - Get User Profile
# =======================

@bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """
    Get user profile information
    
    GET /api/users/1
    Headers: Authorization: Bearer <token>

    Returns:
        200: User profile
        403: Can only view own profile (unless librarian/admin)
        404: User not found
    """

    current_user_id = get_current_user_id()
    current_role = get_current_user_role()

    # Users can only view their own profile unless they are a librarian or admin
    if user_id != current_user_id and current_role not in ['librarian', 'admin']:
        return jsonify({'error': 'You can only view your own profile'}), 403
    
    # Get user from database
    user = execute_query(
        "SELECT user_id, name, email, role, fine_balance FROM Users WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user statistics
    stats = execute_query("""
        SELECT 
            COUNT(CASE WHEN status IN ('active', 'overdue') THEN 1 END) as currently_borrowed,
            COUNT(CASE WHEN status = 'overdue' THEN 1 END) as overdue_books,
            COUNT(*) as total_books_borrowed
        FROM Loans
        WHERE user_id = %s
    """, (user_id,), fetch_one=True)
    
    # Get pending reservations count
    reservations = execute_query("""
        SELECT COUNT(*) as pending_reservations
        FROM Reservations
        WHERE user_id = %s AND status = 'pending'
    """, (user_id,), fetch_one=True)
    
    # Add stats to user object
    user['stats'] = {
        'total_books_borrowed': stats['total_books_borrowed'] if stats else 0,
        'currently_borrowed': stats['currently_borrowed'] if stats else 0,
        'overdue_books': stats['overdue_books'] if stats else 0,
        'pending_reservations': reservations['pending_reservations'] if reservations else 0
    }

    return jsonify(user), 200

# =================================
# PUT /api/users/{user_id} - Update user profile
# =================================

@bp.route('/<int:user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    """
    Update user profile

    PUT /api/users/1
    Headers: Authorization: Bearer <token>
    Body: {
        "name": "John Doe",
        "email": "john.doe@newEmail.com"
    }

    returns:
        200: Profile updated
        403: Can only update from own profile
        409: Email already in use
    """

    current_user_id = get_current_user_id()

    if current_user_id != user_id:
        return jsonify({'error': 'You can only update your own profile'}), 403
    
    data = request.json

    # Validate email if provided
    if data.get('email'):
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if email is currently in use
        existing = execute_query(
            "SELECT user_id FROM Users WHERE email = %s AND user_id != %s",
            (data['email'], user_id),
            fetch_one=True
        )

        if existing:
            return jsonify({'error': 'Email already in use'}), 409
        
    # Build update query dynamically
    updates = []
    params = []

    if data.get('name'):
        updates.append('name = %s')
        params.append(data['name'])
    
    if data.get('email'):
        updates.append('email = %s')
        params.append(data['email'])

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400
    
    # Add user_id to params
    params.append(user_id)

    # Update user
    try:
        execute_query(
            f"UPDATE Users SET {', '.join(updates)} WHERE user_id = %s",
            tuple(params)
        )

        updated_user = execute_query(
            "SELECT user_id, name, email, role, fine_balance FROM Users WHERE user_id = %s",
            (user_id,),
            fetch_one=True
        )

        return jsonify({'message': 'Profile updated successfully',
                        'user': updated_user}), 200
    except Exception as e:
        print(f"Update error: {e}")
        return jsonify({'error': 'Update failed'}), 500
    
# =================================
# GET /api/users - Lists ALL users (Libarian/admin only)
# =================================

@bp.route('', methods=['GET'])
@require_auth
@require_role('librarian', 'admin')
def list_users():
    """
    List all users with optional filters (Libarian/admin only)

    GET /ali/users?search=john&role=student&has_fines=True
    Headers: Authorization: Bearer <token>

    Query Parameters:
        - search: Search by name or email
        - role: Filter by role (student, faculty, librarian, admin)
        - has_fines: Filter users with undpaid fines (True/False)
        - limit: Max results (Default: 50)
        - offset: skip results (default 0)

    Returns:
        200: List of users
    """

    # Get query parameters
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '').strip()
    has_fines = request.args.get('has_fines', '').strip()
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    # Build query
    query = """
        SELECT
            u.user_id,
            u.name,
            u.email,
            u.role,
            u.fine_balance,
            u.create_at,
            COUNT(CASE WHEN l.status IN ('active', 'overdue') THEN l END) as active_loans
            COUNT(CASE WHEN l.status = 'overdue' THEN l END) as overdue_books\
        FROM Users u 
            LEFT JOIN loans l ON u.user_id = l.user_id
        WHERE 1=1
            """
    params = []

    if search:
        query += " AND (u.name LIKE %s OR u.email LIKE %s)"
        search_term = f"%{search}"
        params.extend([search_term, search_term])
    
    if role_filter:
        query +=  " AND u.role = %s"
        params.append(role_filter)

    if has_fines == 'true':
        query += " AND u.fine_balance > 0"
    elif has_fines == 'false':
        query += " AND u.fines_balance = 0"

    # Group by and order
    query += """
        GROUP BY u.user_id
        ORDER BY u.created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    try:
        users = execute_query(query, tuple(params))

        if users is None:
            users = []

        return jsonify({
            'users': users,
            'count': len(users),
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500
    
# ==================================
# PUT /api/users/{user_id}/role - Change user role (admin)
# ==================================

@bp.route('/<int:user_id>/role', methods=['PUT'])
@require_auth
@require_role('admin')
def change_user_role(user_id):
    """
    Change user's role (Admin only)

    PUT /api/users/1/role
    Headers: Authorization: Bearer <token>
    Body: {
        "role": "librarian"
    }

    Valid roles: student, faculty, librarian, admin

    Returns:
        200: Role updated
        400: Invalid role
        404: User not found
    """

    data = request.json

    # Validate role
    valid_roles = ['student', 'faculty', 'librarian', 'admin']
    new_role = data.get('role')

    if not new_role:
        return jsonify({'error': 'Role is required'}), 400
    
    if new_role not in valid_roles:
        return jsonify({'error': f'Invalid role: Must be one of : {", ".join(valid_roles)}'}), 400
    
    user = execute_query(
                         "SELECT user_id, role FROM Users WHERE user_id = %s",
                         (user_id,),
                         fetch_one=True)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    execute_query(
        "UPDATE Users SET role = %s WHERE user_id = %s",
        (new_role, user_id)
    )

    return jsonify({
        'message': 'User role updated successfully',
        'user_id': user_id,
        'old_role': user['role'],
        'new_role': new_role
    }), 200

# ===================================
# GET /api/users/{user_id}/activity - Get User activity (Librarian/Admin)
# ===================================

@bp.route('/<int:user_id>/activity', methods=['GET'])
@require_auth
@require_role('librarian', 'admin')
def get_user_activity(user_id):
    """
        Get user's activity history (Librarian/Admin only)

        GET /api/users/1/activity
        Headers: Authorization: Bearer <token>

        Returns:
            200: Activity history
            404: User not found
    """

    user = execute_query(
        "SELECT user_id, name, email FROM Users WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )

    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    recent_loans = execute_query("""
        SELECT
            l.loan_id,
            l.checkout_date,
            l.due_date,
            l.return_date,
            l.status,
            b.title AS book_title,
            b.author AS book_author,
            b.ISBN
        FROM Loans l 
            JOIN Books b ON l.book_id = b.book_id
        WHERE l.user_id = %s
        ORDER BY l.checkout_date DESC
        LIMIT 10
        """, (user_id,))
    
    recent_fines = execute_query("""
        SELECT 
            f.fine_id,
            f.amount,
            f.issued_at,
            f.paid_at,
            f.paid_status,
            b.title AS book_title
            b.author AS book_author
        FROM Fines f 
            JOIN Loans l ON f.load_Id = l.load_id
            JOIN Books b ON l.book_id = b.book_id
        WHERE f.user_id = %s
        ORDER BY f.issued_at DESC
        LIMIT 10
        """, (user_id,))
    
    active_reservations = execute_query("""
        SELECT 
            r.reservation_id,
            r.reservation_date,
            r.status,
            b.title as book_title,
            b.author as book_author,
            b.ISBN
        FROM Reservations r
            JOIN Books b ON r.book_id = b.book_id
        WHERE r.user_id = %s AND r.status = 'pending'
        ORDER BY r.reservation_date DESC
    """, (user_id,), fetch_all=True)

    reading_list = execute_query("""
        SELECT 
            rl.list_id,
            rl.added_at,
            b.book_id,
            b.title,
            b.author,
            b.ISBN
        FROM ReadingLists rl
            JOIN Books b ON rl.book_id = b.book_id
        WHERE rl.user_id = %s
        ORDER BY rl.added_at DESC
    """, (user_id,))

    return jsonify({
        'user': user,
        'recent_loans': recent_loans if recent_loans else [],
        'recent_fines': recent_fines if recent_fines else [],
        'active_reservations': active_reservations if active_reservations else [],
        'reading_list': reading_list if reading_list else []
    }), 200

# ============================================
# DELETE /api/users/{user_id} - Delete User (Admin)
# ============================================

@bp.route('/<int:user_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_user(user_id):
    """
    Delete user account (Admin only)
    
    DELETE /api/users/1
    Headers: Authorization: Bearer <token>
    
    Returns:
        200: User deleted
        400: Cannot delete user with active loans
        404: User not found
    """
    # Check if user exists
    user = execute_query(
        "SELECT user_id, name FROM Users WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check for active loans using the ActiveLoans view
    active_loans = execute_query("""
        SELECT COUNT(*) as count 
        FROM Loans 
        WHERE user_id = %s AND status IN ('active', 'overdue')
    """, (user_id,), fetch_one=True)
    
    if active_loans and active_loans['count'] > 0:
        return jsonify({
            'error': 'Cannot delete user with active loans',
            'active_loans': active_loans['count']
        }), 400
    
    # Delete user (CASCADE will handle related records)
    execute_query("DELETE FROM Users WHERE user_id = %s", (user_id,))
    
    return jsonify({
        'message': 'User deleted successfully',
        'user_id': user_id,
        'name': user['name']
    }), 200

# ============================================
# GET /api/users/stats - Get User Statistics (Admin)
# ============================================

@bp.route('/stats', methods=['GET'])
@require_auth
@require_role('admin')
def get_user_stats():
    """
    Get overall user statistics (Admin only)
    
    GET /api/users/stats
    Headers: Authorization: Bearer <token>
    
    Returns:
        200: User statistics
    """
    # Get basic user stats
    stats = execute_query("""
        SELECT 
            COUNT(*) as total_users,
            COUNT(CASE WHEN role = 'student' THEN 1 END) as students,
            COUNT(CASE WHEN role = 'faculty' THEN 1 END) as faculty,
            COUNT(CASE WHEN role = 'librarian' THEN 1 END) as librarians,
            COUNT(CASE WHEN role = 'admin' THEN 1 END) as admins,
            COUNT(CASE WHEN fine_balance > 0 THEN 1 END) as users_with_fines,
            SUM(fine_balance) as total_outstanding_fines
        FROM Users
    """, fetch_one=True)
    
    # Get users with overdue books
    overdue_users = execute_query("""
        SELECT COUNT(DISTINCT user_id) as count
        FROM Loans
        WHERE status = 'overdue'
    """, fetch_one=True)
    
    # Get users with active loans
    active_borrowers = execute_query("""
        SELECT COUNT(DISTINCT user_id) as count
        FROM Loans
        WHERE status IN ('active', 'overdue')
    """, fetch_one=True)
    
    stats['users_with_overdue'] = overdue_users['count'] if overdue_users else 0
    stats['active_borrowers'] = active_borrowers['count'] if active_borrowers else 0
    
    return jsonify(stats), 200

# ============================================
# GET /api/users/with-fines - Users with Unpaid Fines (Librarian/Admin)
# ============================================

@bp.route('/with-fines', methods=['GET'])
@require_auth
@require_role('librarian', 'admin')
def get_users_with_fines():
    """
    Get all users with unpaid fines (Librarian/Admin only)
    Uses the UnpaidFines view for efficiency
    
    GET /api/users/with-fines
    Headers: Authorization: Bearer <token>
    
    Returns:
        200: List of users with unpaid fines
    """
    # Use the UnpaidFines view from your schema
    users_with_fines = execute_query("""
        SELECT 
            user_id,
            name,
            email,
            total_owed
        FROM UnpaidFines
        ORDER BY total_owed DESC
    """, fetch_all=True)
    
    if users_with_fines is None:
        users_with_fines = []
    
    return jsonify({
        'users': users_with_fines,
        'count': len(users_with_fines)
    }), 200

# ============================================
# GET /api/users/{user_id}/loans - Get User's Loans
# Uses the ActiveLoans VIEW from your schema
# ============================================

@bp.route('/<int:user_id>/loans', methods=['GET'])
@require_auth
def get_user_loans(user_id):
    """
    Get user's loan history
    
    GET /api/users/1/loans?status=active
    Headers: Authorization: Bearer <token>
    
    Query Parameters:
        - status: Filter by status (active, returned, overdue)
    
    Returns:
        200: List of loans
        403: Can only view own loans
    """
    current_user_id = get_current_user_id()
    current_role = get_current_user_role()
    
    # Users can only view their own loans unless they're librarian/admin
    if current_user_id != user_id and current_role not in ['librarian', 'admin']:
        return jsonify({'error': 'You can only view your own loans'}), 403
    
    # Get status filter
    status_filter = request.args.get('status', '').strip()
    
    # Build query
    if status_filter in ['active', 'overdue']:
        # Use ActiveLoans view for active/overdue loans
        query = """
            SELECT 
                loan_id,
                borrower as name,
                email,
                title,
                ISBN,
                checkout_date,
                due_date,
                days_overdue
            FROM ActiveLoans
            WHERE email = (SELECT email FROM Users WHERE user_id = %s)
        """
        
        if status_filter == 'overdue':
            query += " AND days_overdue > 0"
        elif status_filter == 'active':
            query += " AND days_overdue <= 0"
        
        loans = execute_query(query, (user_id,), fetch_all=True)
    else:
        # Get all loans
        query = """
            SELECT 
                l.loan_id,
                l.checkout_date,
                l.due_date,
                l.return_date,
                l.status,
                b.title,
                b.author,
                b.ISBN,
                DATEDIFF(CURRENT_DATE, l.due_date) as days_overdue
            FROM Loans l
                JOIN Books b ON l.book_id = b.book_id
            WHERE l.user_id = %s
        """

        if status_filter:
            query += " AND l.status = %s"
            loans = execute_query(query, (user_id, status_filter), fetch_all=True)
        else:
            loans = execute_query(query, (user_id,), fetch_all=True)
    
    if loans is None:
        loans = []
    
    return jsonify({
        'loans': loans,
        'count': len(loans)
    }), 200
