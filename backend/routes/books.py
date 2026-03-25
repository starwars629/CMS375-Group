from flask import Blueprint, request, jsonify
from utils.auth import require_auth, require_role
from utils.database import execute_query

bp = Blueprint('books', __name__, url_prefix='/api/books')

@bp.route('', methods=['POST'])
#@require_auth               # Must be logged in
#@require_role('librarian')  # Must be a librarian
def add_book():
    """
    Add a new book to the catalog (Librarians only)

    POST /api/books

    Returns:
    201: Book added successfully
    400: Validation error
    401: Not authenticated
    403: Not a librarian
    409: ISBN already exists
    """
    # 1. Get data from request
    data = request.json

    # Validate required fields
    errors = ''
    if not data.get('ISBN'):
        error += '| ISBN is required'
    if not data.get('title'):
        error += '| Title is required'
    if not data.get('author'):
        error += '| Author is required'
    if not data.get('category'):
        error += '| Category is required'
    if not data.get('publication_year'):
        error += '| Publishing year is required'
    if not data.get('total_copies'):
        error += '| Number of copies is required'
    
    if len(errors != 0):
        return jsonify({'error': errors}), 400
    
    # Validate that book does not exist already
    existing_book = execute_query(
        "SELECT book_id FROM books WHERE ISBN = %s",
        (data['ISBN'],),
        fetch_one = True
    )

    if existing_book:
        return jsonify({'error': 'Book with this ISBN already exists'}), 409
    
    # Validate formatting
    isbn = data['ISBN'].replace('-', '').replace(' ', '')
    if not (len(isbn) == 10 or len(isbn) == 13):
        return jsonify({'error': 'Invalid ISBN format. Must be 10 or 13 digits'}), 400
    
    if data['total_copies'] < 1:
        return jsonify({'error': 'Total copies must be at least 1'}), 400

    # 2. Insert data into database
    query = """
            INSERT INTO books (ISBN, title, author, category, publishing_year, total_copies, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    try:
        book_id = execute_query(query, (
            data['ISBN'],
            data['title'],
            data['author'],
            data['category'],
            data['publication_year'],
            data['total_copies'],
            data['total_copies'] # available copies = initial total_copies
        ))

        # 3. Return response
        if book_id:
            # log action
            print(f"Book added: {data['ISBN']} (ID: {book_id}) by {request.current_user['name']}")

            return jsonify ({
                'message': 'Book added successfully',
                'book_id': book_id
            }), 201
        else:
            return jsonify({'error': 'Failed to add book'}), 500
    
    except Exception as e:
        print(f"Error adding book: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
