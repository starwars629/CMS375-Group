from flask import Flask, jsonify
from datetime import datetime
from flask_cors import CORS
from routes import auth, books, fines, loans, reservations, users
from utils.database import init_db

app = Flask(__name__)
CORS(app)   # Allow frontend to connect

# Initialize database connection
init_db()

# Register route blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(books.bp)
app.register_blueprint(fines.bp)
app.register_blueprint(loans.bp)
app.register_blueprint(reservations.bp)
app.register_blueprint(users.bp)

@app.route('/')
def home():
    """
    API home page with complete endpoint documentation
    """
    return jsonify({
        'message': 'Library Management System API',
        'version': '1.0.0',
        'status': 'running',
        'documentation': '/api/docs',
        
        'endpoints': {
            'authentication': {
                'register': {
                    'method': 'POST',
                    'path': '/api/auth/register',
                    'auth_required': False,
                    'description': 'Register a new user account'
                },
                'login': {
                    'method': 'POST',
                    'path': '/api/auth/login',
                    'auth_required': False,
                    'description': 'Login and receive JWT token'
                },
                'logout': {
                    'method': 'POST',
                    'path': '/api/auth/logout',
                    'auth_required': True,
                    'description': 'Logout current user'
                },
                'change_password': {
                    'method': 'POST',
                    'path': '/api/auth/change-password',
                    'auth_required': True,
                    'description': 'Change user password'
                }
            },
            
            'books': {
                'list_books': {
                    'method': 'GET',
                    'path': '/api/books',
                    'auth_required': False,
                    'description': 'List/search all books',
                    'params': ['query', 'genre', 'available', 'limit', 'offset']
                },
                'get_book': {
                    'method': 'GET',
                    'path': '/api/books/{book_id}',
                    'auth_required': False,
                    'description': 'Get single book details'
                },
                'add_book': {
                    'method': 'POST',
                    'path': '/api/books',
                    'auth_required': True,
                    'role_required': 'librarian',
                    'description': 'Add new book to catalog'
                }
            },
            
            'users': {
                'get_my_profile': {
                    'method': 'GET',
                    'path': '/api/users/me',
                    'auth_required': True,
                    'description': 'Get current user profile'
                },
                'get_user': {
                    'method': 'GET',
                    'path': '/api/users/{user_id}',
                    'auth_required': True,
                    'description': 'Get user profile by ID'
                },
                'update_user': {
                    'method': 'PUT',
                    'path': '/api/users/{user_id}',
                    'auth_required': True,
                    'description': 'Update user profile'
                },
                'list_users': {
                    'method': 'GET',
                    'path': '/api/users',
                    'auth_required': True,
                    'role_required': 'librarian',
                    'description': 'List all users with filters',
                    'params': ['search', 'role', 'has_fines', 'limit', 'offset']
                },
                'change_role': {
                    'method': 'PUT',
                    'path': '/api/users/{user_id}/role',
                    'auth_required': True,
                    'role_required': 'admin',
                    'description': 'Change user role'
                },
                'user_activity': {
                    'method': 'GET',
                    'path': '/api/users/{user_id}/activity',
                    'auth_required': True,
                    'role_required': 'librarian',
                    'description': 'Get user activity history'
                },
                'delete_user': {
                    'method': 'DELETE',
                    'path': '/api/users/{user_id}',
                    'auth_required': True,
                    'role_required': 'admin',
                    'description': 'Delete user account'
                },
                'user_stats': {
                    'method': 'GET',
                    'path': '/api/users/stats',
                    'auth_required': True,
                    'role_required': 'admin',
                    'description': 'Get overall user statistics'
                },
                'users_with_fines': {
                    'method': 'GET',
                    'path': '/api/users/with-fines',
                    'auth_required': True,
                    'role_required': 'librarian',
                    'description': 'Get users with unpaid fines'
                },
                'user_loans': {
                    'method': 'GET',
                    'path': '/api/users/{user_id}/loans',
                    'auth_required': True,
                    'description': 'Get user loan history',
                    'params': ['status']
                }
            },
            
            'loans': {
                'checkout': {
                    'method': 'POST',
                    'path': '/api/loans/checkout',
                    'auth_required': True,
                    'description': 'Check out a book'
                },
                'return': {
                    'method': 'POST',
                    'path': '/api/loans/{loan_id}/return',
                    'auth_required': True,
                    'description': 'Return a checked out book'
                },
                'renew': {
                    'method': 'POST',
                    'path': '/api/loans/{loan_id}/renew',
                    'auth_required': True,
                    'description': 'Renew an active loan'
                },
                'active_loans': {
                    'method': 'GET',
                    'path': '/api/loans/active',
                    'auth_required': True,
                    'role_required': 'librarian',
                    'description': 'Get all active loans'
                },
                'overdue_loans': {
                    'method': 'GET',
                    'path': '/api/loans/overdue',
                    'auth_required': True,
                    'role_required': 'librarian',
                    'description': 'Get all overdue loans'
                }
            },

            'reservations': {
                'status': 'Coming soon'
            },

            'fines': {
                'status': 'Coming soon'
            }
        },
        
        'authentication': {
            'type': 'JWT (JSON Web Token)',
            'header': 'Authorization: Bearer <token>',
            'token_expiration': '24 hours',
            'how_to_get_token': 'POST /api/auth/login with email and password'
        },
        
        'roles': {
            'student': 'Default role for new users',
            'faculty': 'Faculty members with extended borrowing privileges',
            'librarian': 'Can manage books, view all users, manage fines',
            'admin': 'Full system access, can change user roles'
        },
        
        'quick_start': {
            '1': 'Register: POST /api/auth/register',
            '2': 'Login: POST /api/auth/login',
            '3': 'Use token: Add "Authorization: Bearer <token>" header to requests',
            '4': 'Search books: GET /api/books?query=search_term',
            '5': 'View profile: GET /api/users/me'
        },
        
        'team': {
            'backend': 'Andrew',
            'frontend': 'Ethan',
            'database': 'Mauricio'
        },
        
        'resources': {
            'full_documentation': 'See API_Documentation.md',
            'health_check': '/health',
            'github': 'https://github.com/your-repo'
        }
    }), 200

@app.route('/api/docs')
def api_docs():
    """
    Lightweight API documentation endpoint
    """
    return jsonify({
        'title': 'Library Management System API',
        'version': '1.0.0',
        'description': 'RESTful API for managing library operations including books, users, loans, reservations, and fines',
        
        'base_url': 'http://localhost:5000',
        
        'authentication': {
            'description': 'Most endpoints require JWT authentication',
            'login_endpoint': 'POST /api/auth/login',
            'header_format': 'Authorization: Bearer <your-token>',
            'token_expiration': '24 hours'
        },
        
        'endpoint_categories': [
            {
                'category': 'Authentication',
                'base_path': '/api/auth',
                'endpoints': [
                    {
                        'name': 'Register',
                        'method': 'POST',
                        'path': '/register',
                        'auth': False,
                        'description': 'Create new user account'
                    },
                    {
                        'name': 'Login',
                        'method': 'POST',
                        'path': '/login',
                        'auth': False,
                        'description': 'Authenticate and receive token'
                    },
                    {
                        'name': 'Logout',
                        'method': 'POST',
                        'path': '/logout',
                        'auth': True,
                        'description': 'Logout current session'
                    },
                    {
                        'name': 'Change Password',
                        'method': 'POST',
                        'path': '/change-password',
                        'auth': True,
                        'description': 'Update user password'
                    }
                ]
            },
            {
                'category': 'Books',
                'base_path': '/api/books',
                'endpoints': [
                    {
                        'name': 'List Books',
                        'method': 'GET',
                        'path': '',
                        'auth': False,
                        'description': 'Get all books with filters',
                        'query_params': ['query', 'genre', 'available', 'limit', 'offset']
                    },
                    {
                        'name': 'Get Book',
                        'method': 'GET',
                        'path': '/{book_id}',
                        'auth': False,
                        'description': 'Get single book details'
                    },
                    {
                        'name': 'Add Book',
                        'method': 'POST',
                        'path': '',
                        'auth': True,
                        'role': 'librarian',
                        'description': 'Add new book (librarian only)'
                    }
                ]
            },
            {
                'category': 'Loans',
                'base_path': '/api/loans',
                'endpoints': [
                    {
                        'name': 'Checkout Book',
                        'method': 'POST',
                        'path': '/checkout',
                        'auth': True,
                        'description': 'Check out a book'
                    },
                    {
                        'name': 'Return Book',
                        'method': 'POST',
                        'path': '/{loan_id}/return',
                        'auth': True,
                        'description': 'Return a checked out book'
                    },
                    {
                        'name': 'Renew Loan',
                        'method': 'POST',
                        'path': '/{loan_id}/renew',
                        'auth': True,
                        'description': 'Renew an active loan'
                    },
                    {
                        'name': 'Active Loans',
                        'method': 'GET',
                        'path': '/active',
                        'auth': True,
                        'role': 'librarian',
                        'description': 'Get all active loans'
                    },
                    {
                        'name': 'Overdue Loans',
                        'method': 'GET',
                        'path': '/overdue',
                        'auth': True,
                        'role': 'librarian',
                        'description': 'Get all overdue loans'
                    }
                ]
            },
            {
                'category': 'Users',
                'base_path': '/api/users',
                'endpoints': [
                    {
                        'name': 'My Profile',
                        'method': 'GET',
                        'path': '/me',
                        'auth': True,
                        'description': 'Get current user profile'
                    },
                    {
                        'name': 'Get User',
                        'method': 'GET',
                        'path': '/{user_id}',
                        'auth': True,
                        'description': 'Get user by ID'
                    },
                    {
                        'name': 'Update User',
                        'method': 'PUT',
                        'path': '/{user_id}',
                        'auth': True,
                        'description': 'Update user profile'
                    },
                    {
                        'name': 'List Users',
                        'method': 'GET',
                        'path': '',
                        'auth': True,
                        'role': 'librarian',
                        'description': 'List all users (librarian only)'
                    },
                    {
                        'name': 'Change Role',
                        'method': 'PUT',
                        'path': '/{user_id}/role',
                        'auth': True,
                        'role': 'admin',
                        'description': 'Change user role (admin only)'
                    },
                    {
                        'name': 'User Activity',
                        'method': 'GET',
                        'path': '/{user_id}/activity',
                        'auth': True,
                        'role': 'librarian',
                        'description': 'Get user activity history'
                    },
                    {
                        'name': 'Delete User',
                        'method': 'DELETE',
                        'path': '/{user_id}',
                        'auth': True,
                        'role': 'admin',
                        'description': 'Delete user (admin only)'
                    },
                    {
                        'name': 'User Stats',
                        'method': 'GET',
                        'path': '/stats',
                        'auth': True,
                        'role': 'admin',
                        'description': 'Overall statistics (admin only)'
                    },
                    {
                        'name': 'Users with Fines',
                        'method': 'GET',
                        'path': '/with-fines',
                        'auth': True,
                        'role': 'librarian',
                        'description': 'List users with unpaid fines'
                    },
                    {
                        'name': 'User Loans',
                        'method': 'GET',
                        'path': '/{user_id}/loans',
                        'auth': True,
                        'description': 'Get user loan history'
                    }
                ]
            }
        ],
        
        'error_codes': {
            '200': 'OK - Request successful',
            '201': 'Created - Resource created',
            '400': 'Bad Request - Validation error',
            '401': 'Unauthorized - Authentication required',
            '403': 'Forbidden - Insufficient permissions',
            '404': 'Not Found - Resource not found',
            '409': 'Conflict - Duplicate resource',
            '500': 'Internal Server Error - Server error'
        },
        
        'examples': {
            'register': {
                'method': 'POST',
                'url': 'http://localhost:5000/api/auth/register',
                'body': {
                    'name': 'John Doe',
                    'email': 'john@university.edu',
                    'password': 'SecurePass123'
                }
            },
            'login': {
                'method': 'POST',
                'url': 'http://localhost:5000/api/auth/login',
                'body': {
                    'email': 'john@university.edu',
                    'password': 'SecurePass123'
                }
            },
            'search_books': {
                'method': 'GET',
                'url': 'http://localhost:5000/api/books?query=design&genre=Technology'
            },
            'add_book': {
                'method': 'POST',
                'url': 'http://localhost:5000/api/books',
                'headers': {
                    'Authorization': 'Bearer <your-token>',
                    'Content-Type': 'application/json'
                },
                'body': {
                    'bookIsbn': '978-0132350884',
                    'bookTitle': 'Clean Code',
                    'bookAuthor': 'Robert C. Martin',
                    'bookGenre': 'Technology',
                    'bookYear': 2008,
                    'bookCopies': 3
                }
            }
        }
    }), 200

@app.route('/health')
def health():
    """
    Health check endpoint for monitoring
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Library Management System API',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("Library Management System API")
    print("=" * 60)
    print(f"Server starting...")
    print(f"API running at: http://localhost:5000")
    print(f"Documentation: http://localhost:5000/api/docs")
    print(f"Health check: http://localhost:5000/health")
    print("=" * 60)
    print("\nRegistered Routes:")
    
    # Print all routes on startup
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"  {methods:20s} {rule}")
    
    print("\n" + "=" * 60)
    print("Press CTRL+C to quit")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5000)