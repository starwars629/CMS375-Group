from flask import Blueprint, request, jsonify
from utils.auth import require_auth, require_role, optional_auth, get_current_user
from utils.database import execute_query

bp = Blueprint('books', __name__, url_prefix='/api/books')

# ----------------
# GET /api/books - List/Search books
# ----------------
@bp.route('', methods=['GET'])
def get_books():
    """
    Get list of books with optional filters

    GET /api/books
    GET /api/books?query=harry
    GET /api/books?genre=fiction
    GET /api/books?available=true
    GET /api/books?limit=10
    GET /api/books?offset=1

    Query Parameters: 
    - query: Search term for title, author, or ISBN
    - genre: Filter by genre
    - available: Filter by availability
    - limit: Maximum results (default 50, max 200)
    - offset: For pages (default 0)

    Returns:
    200: List of books
    400: Invalid limit/offset
    500: Database error
    """

    # Get query parameters
    search_query = request.args.get('query', '').strip()
    genre_filter = request.args.get('genre', '').strip()
    available_filter = request.args.get('available', '').strip().lower()

    # FIX: Validate and bound limit/offset to prevent abuse and crashes
    try:
        limit = min(int(request.args.get('limit', 50)), 200)
        offset = max(int(request.args.get('offset', 0)), 0)
    except ValueError:
        return jsonify({'error': 'limit and offset must be integers'}), 400

    # Build SQL query based on dynamic filters
    query = "SELECT * FROM books WHERE 1=1"
    params = []

    # Add search filter
    if search_query:
        query += " AND (title LIKE %s OR author LIKE %s OR ISBN LIKE %s)"
        search_term = f"%{search_query}%"
        params.extend([search_term, search_term, search_term])
    
    if genre_filter:
        query += " AND genre = %s"
        params.append(genre_filter)

    # Add availability filter
    if available_filter == 'true':
        query += ' AND available_copies > 0'

    # Add ordering
    query += ' ORDER BY title ASC'
    
    # Add pages
    query += ' LIMIT %s OFFSET %s'
    params.extend([limit, offset])

    # Execute query
    try:
        books = execute_query(query, tuple(params))

        if books is None:
            books = []
        
        return jsonify({
            'books': books,
            'count': len(books),
            'limit': limit,
            'offset': offset
        }), 200
    except Exception as e:
        print(f'Error fetching books: {e}')
        return jsonify({'error': 'Failed to fetch books'}), 500

# ----------------
# GET /api/books/{id} - Get a single book
# ----------------
@bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Get details of a single book

    GET /api/books/1

    Returns:
    200: Book details
    404: Book not found
    500: Database error
    """

    try:
        book = execute_query(
            "SELECT * FROM books WHERE book_id = %s",
            (book_id,),
            fetch_one=True
        )

        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        return jsonify(book), 200
    except Exception as e:
        print(f'Error fetching book {e}')
        return jsonify({'error': 'Failed to fetch book'}), 500

# ----------------
# POST /api/books - Add a book
# ----------------
@bp.route('', methods=['POST'])
@require_auth               # Must be logged in
@require_role('librarian')  # Must be a librarian
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
    data = request.json

    # Validate required fields
    errors = ''
    if not data.get('bookIsbn'):
        errors += '| ISBN is required'
    if not data.get('bookTitle'):
        errors += '| Title is required'
    if not data.get('bookAuthor'):
        errors += '| Author is required'
    if not data.get('bookGenre'):
        errors += '| Genre is required'
    if not data.get('bookCopies'):
        errors += '| Number of copies is required'
    
    if len(errors) != 0:
        return jsonify({'error': errors}), 400

    # Validate ISBN format before uniqueness check
    isbn = data['bookIsbn'].replace('-', '').replace(' ', '')
    if not (len(isbn) == 10 or len(isbn) == 13):
        return jsonify({'error': 'Invalid ISBN format. Must be 10 or 13 digits'}), 400

    # FIX: was data['total_copies'] which doesn't exist — field is 'bookCopies'
    try:
        book_copies = int(data['bookCopies'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Number of copies must be an integer'}), 400

    if book_copies < 1:
        return jsonify({'error': 'Total copies must be at least 1'}), 400

    # Validate that book does not exist already
    existing_book = execute_query(
        "SELECT book_id FROM books WHERE ISBN = %s",
        (isbn,),
        fetch_one=True
    )
    if existing_book:
        return jsonify({'error': 'Book with this ISBN already exists'}), 409

    # FIX: Column list had 7 columns but 9 values were passed (subject and location
    # were included as values but missing from the column list). Now both are explicit.
    query = """
        INSERT INTO books (ISBN, title, author, genre, subject, total_copies, available_copies, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        book_id = execute_query(query, (
            isbn,
            data['bookTitle'],
            data['bookAuthor'],
            data['bookGenre'],      # stored in 'genre' column
            None,                   # subject (optional, not in request body)
            book_copies,            # total_copies
            book_copies,            # available_copies = initial total
            None                    # location (optional, not in request body)
        ))

        if book_id:
            # FIX: was request.current_user which doesn't exist — use get_current_user()
            current_user = get_current_user()
            print(f"Book added: {isbn} (ID: {book_id}) by {current_user['name']}")

            return jsonify({
                'message': 'Book added successfully',
                'book_id': book_id
            }), 201
        else:
            return jsonify({'error': 'Failed to add book'}), 500

    except Exception as e:
        print(f"Error adding book: {e}")
        return jsonify({'error': 'Database error occurred'}), 500