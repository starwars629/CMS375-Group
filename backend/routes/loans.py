from flask import Blueprint, request, jsonify
from utils.auth import require_auth, require_role, get_current_user, get_current_user_id, get_current_user_role
from utils.database import execute_query
from config import LOAN_PERIODS, FINE_RATE_PER_DAY
from datetime import date, timedelta

bp = Blueprint('loans', __name__, url_prefix='/api/loans')

# LOAN_PERIODS and FINE_RATE_PER_DAY are imported from config.py
 
def get_due_date(role):
    """Calculate due date based on user role."""
    days = LOAN_PERIODS.get(role, 14)
    return date.today() + timedelta(days=days)

# ----------------
# POST /api/loans/checkout - Check out a book
# ----------------
@bp.route('/checkout', methods=['POST'])
@require_auth
def checkout():
    """
    Check out a book.
 
    POST /api/loans/checkout {
        "book_id": 1
    }
 
    Returns:
    201: Loan created successfully
    400: Validation error (no copies available, already borrowed)
    404: Book not found
    500: Database error
    """

    data = request.json
    current_user = get_current_user()
    user_id = current_user['user_id']
    role = current_user['role']
 
    # Validate required fields
    if not data.get('book_id'):
        return jsonify({'error': 'book_id is required'}), 400
 
    book_id = data['book_id']

    # Check book exists and has available copies
    book = execute_query(
        "SELECT book_id, title, available_copies FROM books WHERE book_id = %s",
        (book_id,),
        fetch_one=True
    )

    if not book:
        return jsonify({'error': 'Book not found'}), 404
 
    if book['available_copies'] < 1:
        return jsonify({'error': 'No copies available'}), 400
    
    # Check user doesn't already have this book checked out
    existing_loan = execute_query("""
        SELECT loan_id FROM Loans
        WHERE user_id = %s AND book_id = %s AND status IN ('active', 'overdue')
    """, (user_id, book_id), fetch_one=True)

    if existing_loan:
        return jsonify({'error': 'You already have this book checked out'}), 400
 
    due_date = get_due_date(role)

    try:
        # Create loan
        loan_id = execute_query("""
            INSERT INTO Loans (user_id, book_id, checkout_date, due_date, status)
            VALUES (%s, %s, %s, %s, 'active')
        """, (user_id, book_id, date.today(), due_date))
 
        # Decrement available copies
        execute_query("""
            UPDATE books SET available_copies = available_copies - 1
            WHERE book_id = %s
        """, (book_id,))
 
        return jsonify({
            'message': 'Book checked out successfully',
            'loan_id': loan_id,
            'book_id': book_id,
            'title': book['title'],
            'checkout_date': date.today().isoformat(),
            'due_date': due_date.isoformat()
        }), 201
 
    except Exception as e:
        print(f'Checkout error: {e}')
        return jsonify({'error': 'Checkout failed'}), 500
    
# ----------------
# POST /api/loans/{loan_id}/return - Return a book
# ----------------
@bp.route('/<int:loan_id>/return', methods=['POST'])
@require_auth
def return_book(loan_id):
    """
    Return a checked out book. Auto-generates a fine if overdue ($1.00/day).
 
    POST /api/loans/1/return
 
    Returns:
    200: Book returned (with fine info if applicable)
    400: Loan is not active
    403: Not your loan (unless librarian/admin)
    404: Loan not found
    500: Database error
    """

    user_id = get_current_user_id()
    role = get_current_user_role()

    # Get loan
    loan = execute_query("""
        SELECT l.loan_id, l.user_id, l.book_id, l.due_date, l.status, b.title
        FROM Loans l
            JOIN books b ON l.book_id = b.book_id
        WHERE l.loan_id = %s
    """, (loan_id,), fetch_one=True)
 
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
 
    # Only the borrower or librarian/admin can return
    if loan['user_id'] != user_id and role not in ['librarian', 'admin']:
        return jsonify({'error': 'You can only return your own loans'}), 403
 
    if loan['status'] not in ('active', 'overdue'):
        return jsonify({'error': 'This loan is not active'}), 400
    
    today = date.today()
    due_date = loan['due_date']
 
    # Calculate fine if overdue
    fine_id = None
    fine_amount = 0.00
    days_overdue = (today - due_date).days if today > due_date else 0

    try:
        if days_overdue > 0:
            fine_amount = round(days_overdue * FINE_RATE_PER_DAY, 2)
 
            # Insert fine record
            fine_id = execute_query("""
                INSERT INTO Fines (user_id, loan_id, amount, issued_at, paid_status)
                VALUES (%s, %s, %s, %s, 'unpaid')
            """, (loan['user_id'], loan_id, fine_amount, today))
 
            # Update user's fine balance
            execute_query("""
                UPDATE Users SET fine_balance = fine_balance + %s
                WHERE user_id = %s
            """, (fine_amount, loan['user_id']))
 
        # Mark loan as returned
        execute_query("""
            UPDATE Loans SET status = 'returned', return_date = %s
            WHERE loan_id = %s
        """, (today, loan_id))
 
        # Increment available copies
        execute_query("""
            UPDATE books SET available_copies = available_copies + 1
            WHERE book_id = %s
        """, (loan['book_id'],))
 
        response = {
            'message': 'Book returned successfully',
            'loan_id': loan_id,
            'title': loan['title'],
            'return_date': today.isoformat()
        }
 
        if days_overdue > 0:
            response['fine'] = {
                'fine_id': fine_id,
                'days_overdue': days_overdue,
                'amount': fine_amount,
                'message': f'A fine of ${fine_amount:.2f} has been added to your account'
            }
 
        return jsonify(response), 200
 
    except Exception as e:
        print(f'Return error: {e}')
        return jsonify({'error': 'Return failed'}), 500
    
# ----------------
# POST /api/loans/{loan_id}/renew - Renew a loan
# ----------------
@bp.route('/<int:loan_id>/renew', methods=['POST'])
@require_auth
def renew_loan(loan_id):
    """
    Renew a loan, extending the due date by the user's loan period.
    Cannot renew if the loan is overdue.
 
    POST /api/loans/1/renew
 
    Returns:
    200: Loan renewed with new due date
    400: Cannot renew (overdue or not active)
    403: Not your loan
    404: Loan not found
    500: Database error
    """
    user_id = get_current_user_id()
    role = get_current_user_role()
 
    loan = execute_query("""
        SELECT l.loan_id, l.user_id, l.due_date, l.status, b.title
        FROM Loans l
            JOIN books b ON l.book_id = b.book_id
        WHERE l.loan_id = %s
    """, (loan_id,), fetch_one=True)
 
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
 
    if loan['user_id'] != user_id and role not in ['librarian', 'admin']:
        return jsonify({'error': 'You can only renew your own loans'}), 403
 
    if loan['status'] != 'active':
        return jsonify({'error': 'Only active loans can be renewed'}), 400
 
    # Cannot renew if overdue
    if date.today() > loan['due_date']:
        return jsonify({'error': 'Overdue loans cannot be renewed. Please return the book and pay the fine.'}), 400
 
    # Extend due date from current due date (not from today)
    extension_days = LOAN_PERIODS.get(role, 14)
    new_due_date = loan['due_date'] + timedelta(days=extension_days)
 
    try:
        execute_query("""
            UPDATE Loans SET due_date = %s WHERE loan_id = %s
        """, (new_due_date, loan_id))
 
        return jsonify({
            'message': 'Loan renewed successfully',
            'loan_id': loan_id,
            'title': loan['title'],
            'old_due_date': loan['due_date'].isoformat(),
            'new_due_date': new_due_date.isoformat()
        }), 200
 
    except Exception as e:
        print(f'Renewal error: {e}')
        return jsonify({'error': 'Renewal failed'}), 500
    
# ----------------
# GET /api/loans/active - Get all active loans (Librarian/Admin only)
# ----------------
@bp.route('/active', methods=['GET'])
@require_auth
@require_role('librarian', 'admin')
def get_active_loans():
    """
    Get all currently active loans.
 
    GET /api/loans/active
 
    Returns:
    200: List of active loans
    500: Database error
    """
    try:
        loans = execute_query("""
            SELECT
                l.loan_id,
                l.checkout_date,
                l.due_date,
                l.status,
                u.user_id,
                u.name AS borrower_name,
                u.email AS borrower_email,
                b.book_id,
                b.title,
                b.author,
                b.ISBN,
                DATEDIFF(CURRENT_DATE, l.due_date) AS days_overdue
            FROM Loans l
                JOIN Users u ON l.user_id = u.user_id
                JOIN books b ON l.book_id = b.book_id
            WHERE l.status IN ('active', 'overdue')
            ORDER BY l.due_date ASC
        """)
 
        if loans is None:
            loans = []
 
        return jsonify({
            'loans': loans,
            'count': len(loans)
        }), 200
 
    except Exception as e:
        print(f'Error fetching active loans: {e}')
        return jsonify({'error': 'Failed to fetch active loans'}), 500
    
# ----------------
# GET /api/loans/overdue - Get all overdue loans (Librarian/Admin only)
# ----------------
@bp.route('/overdue', methods=['GET'])
@require_auth
@require_role('librarian', 'admin')
def get_overdue_loans():
    """
    Get all overdue loans.
 
    GET /api/loans/overdue
 
    Returns:
    200: List of overdue loans with days overdue and accrued fine
    500: Database error
    """
    try:
        loans = execute_query("""
            SELECT
                l.loan_id,
                l.checkout_date,
                l.due_date,
                u.user_id,
                u.name AS borrower_name,
                u.email AS borrower_email,
                b.book_id,
                b.title,
                b.author,
                b.ISBN,
                DATEDIFF(CURRENT_DATE, l.due_date) AS days_overdue,
                ROUND(DATEDIFF(CURRENT_DATE, l.due_date) * %s, 2) AS accrued_fine
            FROM Loans l
                JOIN Users u ON l.user_id = u.user_id
                JOIN books b ON l.book_id = b.book_id
            WHERE l.status = 'overdue'
               OR (l.status = 'active' AND l.due_date < CURRENT_DATE)
            ORDER BY l.due_date ASC
        """, (FINE_RATE_PER_DAY,))
 
        if loans is None:
            loans = []
 
        return jsonify({
            'loans': loans,
            'count': len(loans)
        }), 200
 
    except Exception as e:
        print(f'Error fetching overdue loans: {e}')
        return jsonify({'error': 'Failed to fetch overdue loans'}), 500