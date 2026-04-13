from flask import Blueprint, request, jsonify
from utils.auth import require_auth, get_current_user, get_current_user_id, get_current_user_role
from utils.database import execute_query
from datetime import date

bp = Blueprint('reservations', __name__, url_prefix='/api/reservations')

# Maximum active reservations per role
RESERVATION_LIMITS = {
    'student': 1,
    'faculty': 3,
    'librarian': 3,
    'admin': 3
}


# ----------------
# POST /api/reservations - Create a reservation
# ----------------
@bp.route('', methods=['POST'])
@require_auth
def create_reservation():
    """
    Create a reservation for a book.

    POST /api/reservations {
        "book_id": 1
    }

    Limits:
    - Student: 1 active reservation
    - Faculty / Librarian / Admin: 3 active reservations

    Returns:
    201: Reservation created
    400: Validation error (already reserved, limit reached, book already available)
    404: Book not found
    500: Database error
    """
    data = request.json
    current_user = get_current_user()
    user_id = current_user['user_id']
    role = current_user['role']

    if not data.get('book_id'):
        return jsonify({'error': 'book_id is required'}), 400

    book_id = data['book_id']

    # Check book exists
    book = execute_query(
        "SELECT book_id, title, available_copies FROM books WHERE book_id = %s",
        (book_id,),
        fetch_one=True
    )

    if not book:
        return jsonify({'error': 'Book not found'}), 404

    # No point reserving a book that's already available
    if book['available_copies'] > 0:
        return jsonify({'error': 'This book is currently available. You can check it out directly.'}), 400

    # Check user doesn't already have a pending reservation for this book
    existing = execute_query("""
        SELECT reservation_id FROM Reservations
        WHERE user_id = %s AND book_id = %s AND status = 'pending'
    """, (user_id, book_id), fetch_one=True)

    if existing:
        return jsonify({'error': 'You already have a pending reservation for this book'}), 400

    # Check user hasn't hit their reservation limit
    limit = RESERVATION_LIMITS.get(role, 1)
    active_count = execute_query("""
        SELECT COUNT(*) as count FROM Reservations
        WHERE user_id = %s AND status = 'pending'
    """, (user_id,), fetch_one=True)

    if active_count and active_count['count'] >= limit:
        return jsonify({
            'error': f'Reservation limit reached. {role.capitalize()}s may have at most {limit} active reservation{"s" if limit > 1 else ""}.'
        }), 400

    try:
        reservation_id = execute_query("""
            INSERT INTO Reservations (user_id, book_id, reservation_date, status)
            VALUES (%s, %s, %s, 'pending')
        """, (user_id, book_id, date.today()))

        return jsonify({
            'message': 'Reservation created successfully',
            'reservation_id': reservation_id,
            'book_id': book_id,
            'title': book['title'],
            'reservation_date': date.today().isoformat(),
            'status': 'pending'
        }), 201

    except Exception as e:
        print(f'Reservation error: {e}')
        return jsonify({'error': 'Failed to create reservation'}), 500


# ----------------
# GET /api/reservations/user/{user_id} - Get a user's reservations
# ----------------
@bp.route('/user/<int:user_id>', methods=['GET'])
@require_auth
def get_user_reservations(user_id):
    """
    Get all reservations for a user.
    Users can only view their own reservations unless librarian/admin.

    GET /api/reservations/user/1
    GET /api/reservations/user/1?status=pending

    Query Parameters:
    - status: Filter by status ('pending', 'fulfilled', 'cancelled')

    Returns:
    200: List of reservations
    403: Not your reservations (unless librarian/admin)
    404: User not found
    500: Database error
    """
    current_user_id = get_current_user_id()
    current_role = get_current_user_role()

    if user_id != current_user_id and current_role not in ['librarian', 'admin']:
        return jsonify({'error': 'You can only view your own reservations'}), 403

    user = execute_query(
        "SELECT user_id FROM Users WHERE user_id = %s",
        (user_id,),
        fetch_one=True
    )
    if not user:
        return jsonify({'error': 'User not found'}), 404

    status_filter = request.args.get('status', '').strip().lower()

    query = """
        SELECT
            r.reservation_id,
            r.reservation_date,
            r.status,
            b.book_id,
            b.title,
            b.author,
            b.ISBN,
            b.available_copies
        FROM Reservations r
            JOIN books b ON r.book_id = b.book_id
        WHERE r.user_id = %s
    """
    params = [user_id]

    if status_filter in ('pending', 'fulfilled', 'cancelled'):
        query += " AND r.status = %s"
        params.append(status_filter)

    query += " ORDER BY r.reservation_date DESC"

    try:
        reservations = execute_query(query, tuple(params))

        if reservations is None:
            reservations = []

        return jsonify({
            'user_id': user_id,
            'reservations': reservations,
            'count': len(reservations)
        }), 200

    except Exception as e:
        print(f'Error fetching reservations: {e}')
        return jsonify({'error': 'Failed to fetch reservations'}), 500


# ----------------
# PUT /api/reservations/{reservation_id}/cancel - Cancel a reservation
# ----------------
@bp.route('/<int:reservation_id>/cancel', methods=['PUT'])
@require_auth
def cancel_reservation(reservation_id):
    """
    Cancel a pending reservation.
    Users can only cancel their own reservations unless librarian/admin.

    PUT /api/reservations/1/cancel

    Returns:
    200: Reservation cancelled
    400: Reservation is not pending
    403: Not your reservation (unless librarian/admin)
    404: Reservation not found
    500: Database error
    """
    current_user_id = get_current_user_id()
    current_role = get_current_user_role()

    reservation = execute_query(
        "SELECT reservation_id, user_id, book_id, status FROM Reservations WHERE reservation_id = %s",
        (reservation_id,),
        fetch_one=True
    )

    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404

    if reservation['user_id'] != current_user_id and current_role not in ['librarian', 'admin']:
        return jsonify({'error': 'You can only cancel your own reservations'}), 403

    if reservation['status'] != 'pending':
        return jsonify({'error': 'Only pending reservations can be cancelled'}), 400

    try:
        execute_query("""
            UPDATE Reservations SET status = 'cancelled'
            WHERE reservation_id = %s
        """, (reservation_id,))

        return jsonify({
            'message': 'Reservation cancelled successfully',
            'reservation_id': reservation_id
        }), 200

    except Exception as e:
        print(f'Cancellation error: {e}')
        return jsonify({'error': 'Failed to cancel reservation'}), 500


# ----------------
# GET /api/reservations/book/{book_id} - Get reservation queue for a book
# ----------------
@bp.route('/book/<int:book_id>', methods=['GET'])
@require_auth
def get_book_reservations(book_id):
    """
    Get the reservation queue for a specific book.
    - Librarian/Admin: sees full queue with borrower details
    - All other authenticated users: sees queue length only

    GET /api/reservations/book/1

    Returns:
    200: Reservation queue (or count only for non-staff)
    404: Book not found
    500: Database error
    """
    current_role = get_current_user_role()

    book = execute_query(
        "SELECT book_id, title, author, available_copies FROM books WHERE book_id = %s",
        (book_id,),
        fetch_one=True
    )

    if not book:
        return jsonify({'error': 'Book not found'}), 404

    try:
        if current_role in ('librarian', 'admin'):
            # Full queue with borrower details
            reservations = execute_query("""
                SELECT
                    r.reservation_id,
                    r.reservation_date,
                    r.status,
                    u.user_id,
                    u.name AS borrower_name,
                    u.email AS borrower_email,
                    u.role
                FROM Reservations r
                    JOIN Users u ON r.user_id = u.user_id
                WHERE r.book_id = %s AND r.status = 'pending'
                ORDER BY r.reservation_date ASC
            """, (book_id,))

            if reservations is None:
                reservations = []

            return jsonify({
                'book_id': book_id,
                'title': book['title'],
                'author': book['author'],
                'available_copies': book['available_copies'],
                'queue': reservations,
                'queue_length': len(reservations)
            }), 200

        else:
            # Queue count only for students/faculty
            result = execute_query("""
                SELECT COUNT(*) as count FROM Reservations
                WHERE book_id = %s AND status = 'pending'
            """, (book_id,), fetch_one=True)

            queue_length = result['count'] if result else 0

            return jsonify({
                'book_id': book_id,
                'title': book['title'],
                'author': book['author'],
                'available_copies': book['available_copies'],
                'queue_length': queue_length
            }), 200

    except Exception as e:
        print(f'Error fetching book reservations: {e}')
        return jsonify({'error': 'Failed to fetch reservation queue'}), 500