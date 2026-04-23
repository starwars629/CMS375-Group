from flask import Blueprint, request, jsonify
from utils.auth import require_auth, require_role, get_current_user_id, get_current_user_role
from utils.database import execute_query
from datetime import date

bp = Blueprint('fines', __name__, url_prefix='/api/fines')


# ----------------
# GET /api/fines/user/{user_id} - Get a user's fines
# ----------------
@bp.route('/user/<int:user_id>', methods=['GET'])
@require_auth
def get_user_fines(user_id):
    """
    Get all fines for a user.
    Users can only view their own fines. Librarians/admins can view any user's fines.

    GET /api/fines/user/1
    GET /api/fines/user/1?status=unpaid

    Query Parameters:
    - status: Filter by paid status ('paid', 'unpaid')

    Returns:
    200: List of fines
    403: Not your fines (unless librarian/admin)
    404: User not found
    500: Database error
    """
    current_user_id = get_current_user_id()
    current_role = get_current_user_role()

    # Users can only view their own fines unless librarian/admin
    if user_id != current_user_id and current_role not in ['librarian', 'admin']:
        return jsonify({'error': 'You can only view your own fines'}), 403

    # Check user exists
    user = execute_query(
        "SELECT user_id, name, fine_balance, total_fines_paid FROM Users WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )
    if not user:
        return jsonify({'error': 'User not found'}), 404

    status_filter = request.args.get('status', '').strip().lower()

    query = """
        SELECT
            f.fine_id,
            f.amount,
            f.issued_at,
            f.paid_at,
            f.paid_status,
            b.title AS book_title,
            b.author AS book_author,
            b.ISBN
        FROM Fines f
            JOIN Loans l ON f.loan_id = l.loan_id
            JOIN Books b ON l.book_id = b.book_id
        WHERE f.user_id = %s
    """
    params = [user_id]

    if status_filter in ('paid', 'unpaid'):
        query += " AND f.paid_status = %s"
        params.append(status_filter)

    query += " ORDER BY f.issued_at DESC"

    try:
        fines = execute_query(query, tuple(params))

        if fines is None:
            fines = []

        return jsonify({
            'user_id': user_id,
            'fine_balance': user['fine_balance'],
            'total_fines_paid': user['total_fines_paid'],
            'fines': fines,
            'count': len(fines)
        }), 200

    except Exception as e:
        print(f'Error fetching fines: {e}')
        return jsonify({'error': 'Failed to fetch fines'}), 500


# ----------------
# POST /api/fines/{fine_id}/pay - Pay a fine
# ----------------
@bp.route('/<int:fine_id>/pay', methods=['POST'])
@require_auth
def pay_fine(fine_id):
    """
    Mark a fine as paid. Users can only pay their own fines.

    POST /api/fines/1/pay

    Returns:
    200: Fine marked as paid
    400: Fine already paid
    403: Not your fine (unless librarian/admin)
    404: Fine not found
    500: Database error
    """
    current_user_id = get_current_user_id()
    current_role = get_current_user_role()

    fine = execute_query(
        "SELECT fine_id, user_id, amount, paid_status FROM Fines WHERE fine_id = %s",
        (fine_id,),
        fetch_one=True
    )

    if not fine:
        return jsonify({'error': 'Fine not found'}), 404

    if fine['user_id'] != current_user_id and current_role not in ['librarian', 'admin']:
        return jsonify({'error': 'You can only pay your own fines'}), 403

    if fine['paid_status'] == 'paid':
        return jsonify({'error': 'This fine has already been paid'}), 400

    try:
        today = date.today()

        # Mark fine as paid
        execute_query("""
            UPDATE Fines SET paid_status = 'paid', paid_at = %s
            WHERE fine_id = %s
        """, (today, fine_id))

        # Deduct from user's fine balance and track total paid
        execute_query("""
            UPDATE Users SET fine_balance = fine_balance - %s, total_fines_paid = total_fines_paid + %s
            WHERE user_id = %s
        """, (fine['amount'], fine['amount'], fine['user_id']))

        return jsonify({
            'message': 'Fine paid successfully',
            'fine_id': fine_id,
            'amount_paid': fine['amount'],
            'paid_at': today.isoformat()
        }), 200

    except Exception as e:
        print(f'Payment error: {e}')
        return jsonify({'error': 'Payment failed'}), 500


# ----------------
# POST /api/fines/{fine_id}/waive - Waive a fine (Librarian/Admin only)
# ----------------
@bp.route('/<int:fine_id>/waive', methods=['POST'])
@require_auth
@require_role('librarian', 'admin')
def waive_fine(fine_id):
    """
    Waive a fine, removing it from the user's balance. Librarian/Admin only.

    POST /api/fines/1/waive

    Returns:
    200: Fine waived successfully
    400: Fine already paid or waived
    404: Fine not found
    500: Database error
    """
    fine = execute_query(
        "SELECT fine_id, user_id, amount, paid_status FROM Fines WHERE fine_id = %s",
        (fine_id,),
        fetch_one=True
    )

    if not fine:
        return jsonify({'error': 'Fine not found'}), 404

    if fine['paid_status'] != 'unpaid':
        return jsonify({'error': 'Only unpaid fines can be waived'}), 400

    try:
        today = date.today()

        # Mark fine as waived
        execute_query("""
            UPDATE Fines SET paid_status = 'waived', paid_at = %s
            WHERE fine_id = %s
        """, (today, fine_id))

        # Remove amount from user's fine balance and track total paid
        execute_query("""
            UPDATE Users SET fine_balance = fine_balance - %s, total_fines_paid = total_fines_paid + %s
            WHERE user_id = %s
        """, (fine['amount'], fine['amount'], fine['user_id']))

        return jsonify({
            'message': 'Fine waived successfully',
            'fine_id': fine_id,
            'amount_waived': fine['amount'],
            'waived_at': today.isoformat()
        }), 200

    except Exception as e:
        print(f'Waive error: {e}')
        return jsonify({'error': 'Failed to waive fine'}), 500


# ----------------
# GET /api/fines/outstanding - Get all outstanding fines (Librarian/Admin only)
# ----------------
@bp.route('/outstanding', methods=['GET'])
@require_auth
@require_role('librarian', 'admin')
def get_outstanding_fines():
    """
    Get all unpaid fines across all users.

    GET /api/fines/outstanding

    Returns:
    200: List of all unpaid fines with total
    500: Database error
    """
    try:
        fines = execute_query("""
            SELECT
                f.fine_id,
                f.amount,
                f.issued_at,
                f.paid_status,
                u.user_id,
                u.name AS borrower_name,
                u.email AS borrower_email,
                b.title AS book_title,
                b.author AS book_author,
                b.ISBN
            FROM Fines f
                JOIN Users u ON f.user_id = u.user_id
                JOIN Loans l ON f.loan_id = l.loan_id
                JOIN Books b ON l.book_id = b.book_id
            WHERE f.paid_status = 'unpaid'
            ORDER BY f.issued_at ASC
        """)

        if fines is None:
            fines = []

        total_outstanding = sum(f['amount'] for f in fines)

        return jsonify({
            'fines': fines,
            'count': len(fines),
            'total_outstanding': round(total_outstanding, 2)
        }), 200

    except Exception as e:
        print(f'Error fetching outstanding fines: {e}')
        return jsonify({'error': 'Failed to fetch outstanding fines'}), 500