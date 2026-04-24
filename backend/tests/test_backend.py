"""
Library Management System - Backend Test Suite
===============================================
Run with:  pytest tests/test_backend.py -v
           (from the backend/ directory)

All database calls are mocked so no real DB connection is needed.
"""

import sys
import os
import json
import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

# Make sure the backend/ directory is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Prevent init_db() from trying to connect to a real database on import
with patch('utils.database.init_db'):
    from app import app
from utils.auth import create_token


# ============================================================
# Fixtures & Helpers
# ============================================================

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def auth_header(user_id=1, role='student', name='Alice Johnson', email='alice@university.edu'):
    """Return an Authorization header dict with a real JWT for the given user."""
    token = create_token(user_id=user_id, role=role, name=name, email=email)
    return {'Authorization': f'Bearer {token}'}


def librarian_header():
    return auth_header(user_id=10, role='librarian', name='Carol White', email='carol@university.edu')


def admin_header():
    return auth_header(user_id=99, role='admin', name='David Admin', email='david@university.edu')


# ============================================================
# Health & Home
# ============================================================

class TestHealth:
    def test_health_check(self, client):
        r = client.get('/health')
        assert r.status_code == 200
        assert r.get_json()['status'] == 'healthy'

    def test_home_returns_endpoint_map(self, client):
        r = client.get('/')
        assert r.status_code == 200
        data = r.get_json()
        assert 'endpoints' in data
        assert 'authentication' in data['endpoints']

    def test_api_docs(self, client):
        r = client.get('/api/docs')
        assert r.status_code == 200
        assert 'endpoint_categories' in r.get_json()


# ============================================================
# Authentication
# ============================================================

class TestAuthRegister:
    ROUTE = '/api/auth/register'

    def test_register_success(self, client):
        with patch('routes.auth.execute_query') as mock_q, \
             patch('routes.auth.hash_password', return_value='hashed_pw'):
            mock_q.side_effect = [None, 42]   # email check → no user; INSERT → new id
            r = client.post(self.ROUTE, json={
                'name': 'John Doe',
                'email': 'john@university.edu',
                'password': 'SecurePass123'
            })
        assert r.status_code == 201
        assert r.get_json()['user_id'] == 42

    def test_register_missing_fields(self, client):
        r = client.post(self.ROUTE, json={'email': 'john@university.edu'})
        assert r.status_code == 400
        assert 'error' in r.get_json()

    def test_register_invalid_email(self, client):
        r = client.post(self.ROUTE, json={
            'name': 'John', 'email': 'not-an-email', 'password': 'SecurePass123'
        })
        assert r.status_code == 400

    def test_register_weak_password(self, client):
        r = client.post(self.ROUTE, json={
            'name': 'John', 'email': 'john@university.edu', 'password': 'abc'
        })
        assert r.status_code == 400

    def test_register_duplicate_email(self, client):
        with patch('routes.auth.execute_query', return_value={'user_id': 1}):
            r = client.post(self.ROUTE, json={
                'name': 'John', 'email': 'john@university.edu', 'password': 'SecurePass123'
            })
        assert r.status_code == 409

    def test_register_sanitizes_name_input(self, client):
        with patch('routes.auth.execute_query') as mock_q, \
             patch('routes.auth.hash_password', return_value='hashed_pw'):
            mock_q.side_effect = [None, 100]
            r = client.post(self.ROUTE, json={
                'name': '<script>alert(1)</script>John',
                'email': 'john@university.edu',
                'password': 'SecurePass123'
            })
        assert r.status_code == 201
        insert_call = mock_q.call_args_list[1]
        inserted_name = insert_call.args[1][0]
        assert '<script>' not in inserted_name
        assert 'alert(1)' in inserted_name


class TestAuthLogin:
    ROUTE = '/api/auth/login'

    def test_login_success(self, client):
        fake_user = {
            'user_id': 1, 'name': 'Alice', 'email': 'alice@university.edu',
            'password': 'hashed_pw', 'role': 'student', 'fine_balance': 0.00
        }
        with patch('routes.auth.execute_query', return_value=fake_user), \
             patch('routes.auth.verify_password', return_value=True):
            r = client.post(self.ROUTE, json={
                'email': 'alice@university.edu', 'password': 'SecurePass123'
            })
        assert r.status_code == 200
        data = r.get_json()
        assert 'token' in data
        assert 'password' not in data['user']

    def test_login_missing_fields(self, client):
        r = client.post(self.ROUTE, json={'email': 'alice@university.edu'})
        assert r.status_code == 400

    def test_login_user_not_found(self, client):
        with patch('routes.auth.execute_query', return_value=None):
            r = client.post(self.ROUTE, json={
                'email': 'nobody@university.edu', 'password': 'SecurePass123'
            })
        assert r.status_code == 401

    def test_login_wrong_password(self, client):
        fake_user = {
            'user_id': 1, 'name': 'Alice', 'email': 'alice@university.edu',
            'password': 'hashed_pw', 'role': 'student', 'fine_balance': 0.00
        }
        with patch('routes.auth.execute_query', return_value=fake_user), \
             patch('routes.auth.verify_password', return_value=False):
            r = client.post(self.ROUTE, json={
                'email': 'alice@university.edu', 'password': 'WrongPassword1'
            })
        assert r.status_code == 401


class TestAuthLogout:
    def test_logout_success(self, client):
        r = client.post('/api/auth/logout', headers=auth_header())
        assert r.status_code == 200
        assert 'Logged out' in r.get_json()['message']

    def test_logout_no_token(self, client):
        r = client.post('/api/auth/logout')
        assert r.status_code == 401


class TestAuthChangePassword:
    ROUTE = '/api/auth/change-password'

    def test_change_password_success(self, client):
        with patch('routes.auth.execute_query') as mock_q, \
             patch('routes.auth.verify_password', return_value=True), \
             patch('routes.auth.hash_password', return_value='new_hashed'):
            mock_q.side_effect = [{'password': 'old_hashed'}, None]
            r = client.post(self.ROUTE,
                            headers=auth_header(),
                            json={'current_password': 'OldPass123', 'new_password': 'NewPass456'})
        assert r.status_code == 200

    def test_change_password_wrong_current(self, client):
        with patch('routes.auth.execute_query', return_value={'password': 'old_hashed'}), \
             patch('routes.auth.verify_password', return_value=False):
            r = client.post(self.ROUTE,
                            headers=auth_header(),
                            json={'current_password': 'WrongOld1', 'new_password': 'NewPass456'})
        assert r.status_code == 401

    def test_change_password_missing_fields(self, client):
        r = client.post(self.ROUTE, headers=auth_header(), json={'current_password': 'OldPass123'})
        assert r.status_code == 400


# ============================================================
# Books
# ============================================================

class TestBooks:
    FAKE_BOOK = {
        'book_id': 1, 'ISBN': '978-0132350884', 'title': 'Clean Code',
        'author': 'Robert C. Martin', 'genre': 'Technology',
        'subject': 'Software Engineering', 'total_copies': 3,
        'available_copies': 3, 'location': 'Section A', 'created_at': '2026-01-01'
    }

    def test_list_books(self, client):
        with patch('routes.books.execute_query', return_value=[self.FAKE_BOOK]):
            r = client.get('/api/books')
        assert r.status_code == 200
        assert r.get_json()['count'] == 1

    def test_list_books_empty(self, client):
        with patch('routes.books.execute_query', return_value=[]):
            r = client.get('/api/books')
        assert r.status_code == 200
        assert r.get_json()['books'] == []

    def test_list_books_invalid_limit(self, client):
        r = client.get('/api/books?limit=abc')
        assert r.status_code == 400

    def test_get_book_found(self, client):
        with patch('routes.books.execute_query', return_value=self.FAKE_BOOK):
            r = client.get('/api/books/1')
        assert r.status_code == 200
        assert r.get_json()['title'] == 'Clean Code'

    def test_get_book_not_found(self, client):
        with patch('routes.books.execute_query', return_value=None):
            r = client.get('/api/books/999')
        assert r.status_code == 404

    def test_add_book_success(self, client):
        with patch('routes.books.execute_query') as mock_q, \
             patch('routes.books.get_current_user', return_value={'name': 'Carol'}):
            mock_q.side_effect = [None, 5]   # ISBN check → not found; INSERT → new id
            r = client.post('/api/books',
                            headers=librarian_header(),
                            json={
                                'bookIsbn': '978-0451524935',
                                'bookTitle': '1984',
                                'bookAuthor': 'George Orwell',
                                'bookGenre': 'Fiction',
                                'bookCopies': 3
                            })
        assert r.status_code == 201
        assert r.get_json()['book_id'] == 5

    def test_add_book_forbidden_for_student(self, client):
        r = client.post('/api/books', headers=auth_header(), json={
            'bookIsbn': '978-0451524935', 'bookTitle': '1984',
            'bookAuthor': 'George Orwell', 'bookGenre': 'Fiction', 'bookCopies': 1
        })
        assert r.status_code == 403

    def test_add_book_duplicate_isbn(self, client):
        with patch('routes.books.execute_query', return_value={'book_id': 1}):
            r = client.post('/api/books',
                            headers=librarian_header(),
                            json={
                                'bookIsbn': '978-0132350884', 'bookTitle': 'Clean Code',
                                'bookAuthor': 'R. Martin', 'bookGenre': 'Tech', 'bookCopies': 1
                            })
        assert r.status_code == 409

    def test_add_book_missing_fields(self, client):
        r = client.post('/api/books', headers=librarian_header(),
                        json={'bookTitle': 'No ISBN Book'})
        assert r.status_code == 400

    def test_add_book_invalid_isbn(self, client):
        r = client.post('/api/books', headers=librarian_header(), json={
            'bookIsbn': '123', 'bookTitle': 'Test', 'bookAuthor': 'A',
            'bookGenre': 'G', 'bookCopies': 1
        })
        assert r.status_code == 400


# ============================================================
# Loans
# ============================================================

class TestLoans:
    FAKE_BOOK = {'book_id': 1, 'title': 'Clean Code', 'available_copies': 2}
    FAKE_LOAN = {
        'loan_id': 1, 'user_id': 1, 'book_id': 1,
        'due_date': date.today() + timedelta(days=5),
        'status': 'active', 'title': 'Clean Code'
    }

    def test_checkout_success(self, client):
        with patch('routes.loans.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_BOOK, None, 7, None]
            r = client.post('/api/loans/checkout',
                            headers=auth_header(),
                            json={'book_id': 1})
        assert r.status_code == 201
        assert r.get_json()['loan_id'] == 7

    def test_checkout_no_copies(self, client):
        with patch('routes.loans.execute_query', return_value={**self.FAKE_BOOK, 'available_copies': 0}):
            r = client.post('/api/loans/checkout', headers=auth_header(), json={'book_id': 1})
        assert r.status_code == 400
        assert 'No copies' in r.get_json()['error']

    def test_checkout_already_borrowed(self, client):
        with patch('routes.loans.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_BOOK, {'loan_id': 1}]
            r = client.post('/api/loans/checkout', headers=auth_header(), json={'book_id': 1})
        assert r.status_code == 400
        assert 'already have' in r.get_json()['error']

    def test_checkout_book_not_found(self, client):
        with patch('routes.loans.execute_query', return_value=None):
            r = client.post('/api/loans/checkout', headers=auth_header(), json={'book_id': 999})
        assert r.status_code == 404

    def test_checkout_missing_book_id(self, client):
        r = client.post('/api/loans/checkout', headers=auth_header(), json={})
        assert r.status_code == 400

    def test_return_on_time(self, client):
        with patch('routes.loans.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_LOAN, None, None]
            r = client.post('/api/loans/1/return', headers=auth_header())
        assert r.status_code == 200
        assert 'fine' not in r.get_json()

    def test_return_overdue_generates_fine(self, client):
        overdue_loan = {**self.FAKE_LOAN, 'due_date': date.today() - timedelta(days=3), 'status': 'overdue'}
        with patch('routes.loans.execute_query') as mock_q:
            mock_q.side_effect = [overdue_loan, 5, None, None, None]
            r = client.post('/api/loans/1/return', headers=auth_header())
        assert r.status_code == 200
        data = r.get_json()
        assert 'fine' in data
        assert data['fine']['days_overdue'] == 3
        assert data['fine']['amount'] == 3.00

    def test_return_loan_not_found(self, client):
        with patch('routes.loans.execute_query', return_value=None):
            r = client.post('/api/loans/999/return', headers=auth_header())
        assert r.status_code == 404

    def test_return_not_your_loan(self, client):
        other_loan = {**self.FAKE_LOAN, 'user_id': 99}
        with patch('routes.loans.execute_query', return_value=other_loan):
            r = client.post('/api/loans/1/return', headers=auth_header(user_id=1))
        assert r.status_code == 403

    def test_renew_success(self, client):
        with patch('routes.loans.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_LOAN, None]
            r = client.post('/api/loans/1/renew', headers=auth_header())
        assert r.status_code == 200
        assert 'new_due_date' in r.get_json()

    def test_renew_overdue_rejected(self, client):
        overdue_loan = {**self.FAKE_LOAN, 'due_date': date.today() - timedelta(days=1), 'status': 'active'}
        with patch('routes.loans.execute_query', return_value=overdue_loan):
            r = client.post('/api/loans/1/renew', headers=auth_header())
        assert r.status_code == 400
        assert 'Overdue' in r.get_json()['error']

    def test_renew_not_active(self, client):
        returned_loan = {**self.FAKE_LOAN, 'status': 'returned'}
        with patch('routes.loans.execute_query', return_value=returned_loan):
            r = client.post('/api/loans/1/renew', headers=auth_header())
        assert r.status_code == 400

    def test_get_active_loans_librarian(self, client):
        with patch('routes.loans.execute_query', return_value=[]):
            r = client.get('/api/loans/active', headers=librarian_header())
        assert r.status_code == 200

    def test_get_active_loans_forbidden_for_student(self, client):
        r = client.get('/api/loans/active', headers=auth_header())
        assert r.status_code == 403

    def test_get_overdue_loans_librarian(self, client):
        with patch('routes.loans.execute_query', return_value=[]):
            r = client.get('/api/loans/overdue', headers=librarian_header())
        assert r.status_code == 200


# ============================================================
# Reservations
# ============================================================

class TestReservations:
    FAKE_BOOK_UNAVAILABLE = {'book_id': 2, 'title': 'Design Patterns', 'available_copies': 0}
    FAKE_BOOK_AVAILABLE   = {'book_id': 2, 'title': 'Design Patterns', 'available_copies': 2}
    FAKE_RESERVATION = {
        'reservation_id': 1, 'user_id': 1, 'book_id': 2, 'status': 'pending'
    }

    def test_create_reservation_success(self, client):
        with patch('routes.reservations.execute_query') as mock_q:
            mock_q.side_effect = [
                self.FAKE_BOOK_UNAVAILABLE,  # book lookup
                None,                        # existing reservation check
                {'count': 0},                # active count
                1                            # INSERT
            ]
            r = client.post('/api/reservations', headers=auth_header(), json={'book_id': 2})
        assert r.status_code == 201
        assert r.get_json()['status'] == 'pending'

    def test_create_reservation_book_available(self, client):
        with patch('routes.reservations.execute_query', return_value=self.FAKE_BOOK_AVAILABLE):
            r = client.post('/api/reservations', headers=auth_header(), json={'book_id': 2})
        assert r.status_code == 400
        assert 'available' in r.get_json()['error']

    def test_create_reservation_already_reserved(self, client):
        with patch('routes.reservations.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_BOOK_UNAVAILABLE, {'reservation_id': 1}]
            r = client.post('/api/reservations', headers=auth_header(), json={'book_id': 2})
        assert r.status_code == 400
        assert 'already have' in r.get_json()['error']

    def test_create_reservation_limit_reached(self, client):
        with patch('routes.reservations.execute_query') as mock_q:
            mock_q.side_effect = [
                self.FAKE_BOOK_UNAVAILABLE,
                None,
                {'count': 1}   # student limit is 1
            ]
            r = client.post('/api/reservations', headers=auth_header(), json={'book_id': 2})
        assert r.status_code == 400
        assert 'limit' in r.get_json()['error']

    def test_create_reservation_missing_book_id(self, client):
        r = client.post('/api/reservations', headers=auth_header(), json={})
        assert r.status_code == 400

    def test_get_user_reservations(self, client):
        with patch('routes.reservations.execute_query') as mock_q:
            mock_q.side_effect = [{'user_id': 1}, []]
            r = client.get('/api/reservations/user/1', headers=auth_header())
        assert r.status_code == 200

    def test_get_user_reservations_forbidden(self, client):
        with patch('routes.reservations.execute_query', return_value={'user_id': 2}):
            r = client.get('/api/reservations/user/2', headers=auth_header(user_id=1))
        assert r.status_code == 403

    def test_cancel_reservation_success(self, client):
        with patch('routes.reservations.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_RESERVATION, None]
            r = client.put('/api/reservations/1/cancel', headers=auth_header())
        assert r.status_code == 200

    def test_cancel_reservation_not_pending(self, client):
        fulfilled = {**self.FAKE_RESERVATION, 'status': 'fulfilled'}
        with patch('routes.reservations.execute_query', return_value=fulfilled):
            r = client.put('/api/reservations/1/cancel', headers=auth_header())
        assert r.status_code == 400

    def test_cancel_reservation_not_found(self, client):
        with patch('routes.reservations.execute_query', return_value=None):
            r = client.put('/api/reservations/999/cancel', headers=auth_header())
        assert r.status_code == 404

    def test_get_book_queue_student_view(self, client):
        with patch('routes.reservations.execute_query') as mock_q:
            mock_q.side_effect = [
                {'book_id': 2, 'title': 'Design Patterns', 'author': 'GoF', 'available_copies': 0},
                {'count': 3}
            ]
            r = client.get('/api/reservations/book/2', headers=auth_header())
        assert r.status_code == 200
        data = r.get_json()
        assert data['queue_length'] == 3
        assert 'queue' not in data

    def test_get_book_queue_librarian_view(self, client):
        fake_queue = [
            {'reservation_id': 1, 'reservation_date': '2026-04-01', 'status': 'pending',
             'user_id': 1, 'borrower_name': 'Alice', 'borrower_email': 'alice@u.edu', 'role': 'student'}
        ]
        with patch('routes.reservations.execute_query') as mock_q:
            mock_q.side_effect = [
                {'book_id': 2, 'title': 'Design Patterns', 'author': 'GoF', 'available_copies': 0},
                fake_queue
            ]
            r = client.get('/api/reservations/book/2', headers=librarian_header())
        assert r.status_code == 200
        data = r.get_json()
        assert 'queue' in data
        assert data['queue_length'] == 1


# ============================================================
# Fines
# ============================================================

class TestFines:
    FAKE_USER = {'user_id': 1, 'name': 'Alice', 'fine_balance': 4.00}
    FAKE_FINE = {'fine_id': 1, 'user_id': 1, 'amount': 4.00, 'paid_status': 'unpaid'}

    def test_get_user_fines(self, client):
        with patch('routes.fines.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, [self.FAKE_FINE]]
            r = client.get('/api/fines/user/1', headers=auth_header())
        assert r.status_code == 200
        data = r.get_json()
        assert data['count'] == 1
        assert data['fine_balance'] == 4.00

    def test_get_fines_forbidden_for_other_user(self, client):
        r = client.get('/api/fines/user/2', headers=auth_header(user_id=1))
        assert r.status_code == 403

    def test_get_fines_user_not_found(self, client):
        with patch('routes.fines.execute_query', return_value=None):
            r = client.get('/api/fines/user/999', headers=librarian_header())
        assert r.status_code == 404

    def test_pay_fine_success(self, client):
        with patch('routes.fines.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_FINE, None, None]
            r = client.post('/api/fines/1/pay', headers=auth_header())
        assert r.status_code == 200
        assert r.get_json()['amount_paid'] == 4.00

    def test_pay_fine_already_paid(self, client):
        paid_fine = {**self.FAKE_FINE, 'paid_status': 'paid'}
        with patch('routes.fines.execute_query', return_value=paid_fine):
            r = client.post('/api/fines/1/pay', headers=auth_header())
        assert r.status_code == 400

    def test_pay_fine_not_found(self, client):
        with patch('routes.fines.execute_query', return_value=None):
            r = client.post('/api/fines/999/pay', headers=auth_header())
        assert r.status_code == 404

    def test_pay_fine_forbidden(self, client):
        other_fine = {**self.FAKE_FINE, 'user_id': 99}
        with patch('routes.fines.execute_query', return_value=other_fine):
            r = client.post('/api/fines/1/pay', headers=auth_header(user_id=1))
        assert r.status_code == 403

    def test_waive_fine_success(self, client):
        with patch('routes.fines.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_FINE, None, None]
            r = client.post('/api/fines/1/waive', headers=librarian_header())
        assert r.status_code == 200
        assert r.get_json()['amount_waived'] == 4.00

    def test_waive_fine_already_paid(self, client):
        paid_fine = {**self.FAKE_FINE, 'paid_status': 'paid'}
        with patch('routes.fines.execute_query', return_value=paid_fine):
            r = client.post('/api/fines/1/waive', headers=librarian_header())
        assert r.status_code == 400

    def test_waive_fine_forbidden_for_student(self, client):
        r = client.post('/api/fines/1/waive', headers=auth_header())
        assert r.status_code == 403

    def test_get_outstanding_fines(self, client):
        fake_fines = [
            {'fine_id': 1, 'amount': 4.00, 'paid_status': 'unpaid',
             'user_id': 1, 'borrower_name': 'Alice', 'borrower_email': 'alice@u.edu',
             'book_title': 'Clean Code', 'book_author': 'R. Martin', 'ISBN': '978-X',
             'issued_at': '2026-04-01'},
        ]
        with patch('routes.fines.execute_query', return_value=fake_fines):
            r = client.get('/api/fines/outstanding', headers=librarian_header())
        assert r.status_code == 200
        data = r.get_json()
        assert data['total_outstanding'] == 4.00

    def test_get_outstanding_fines_forbidden_for_student(self, client):
        r = client.get('/api/fines/outstanding', headers=auth_header())
        assert r.status_code == 403


# ============================================================
# Users
# ============================================================

class TestUsers:
    FAKE_USER = {
        'user_id': 1, 'name': 'Alice Johnson', 'email': 'alice@university.edu',
        'role': 'student', 'fine_balance': 0.00, 'created_at': '2026-01-15T08:00:00'
    }
    FAKE_STATS = {'currently_borrowed': 2, 'overdue_books': 0, 'total_books_borrowed': 10}
    FAKE_RESERVATIONS = {'pending_reservations': 1}

    def test_get_my_profile(self, client):
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, self.FAKE_STATS, self.FAKE_RESERVATIONS]
            r = client.get('/api/users/me', headers=auth_header())
        assert r.status_code == 200
        data = r.get_json()
        assert data['email'] == 'alice@university.edu'
        assert 'stats' in data

    def test_get_my_profile_unauthenticated(self, client):
        r = client.get('/api/users/me')
        assert r.status_code == 401

    def test_get_user_profile_own(self, client):
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, self.FAKE_STATS, self.FAKE_RESERVATIONS]
            r = client.get('/api/users/1', headers=auth_header(user_id=1))
        assert r.status_code == 200

    def test_get_user_profile_forbidden(self, client):
        r = client.get('/api/users/2', headers=auth_header(user_id=1))
        assert r.status_code == 403

    def test_get_user_profile_librarian_can_view_any(self, client):
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, self.FAKE_STATS, self.FAKE_RESERVATIONS]
            r = client.get('/api/users/1', headers=librarian_header())
        assert r.status_code == 200

    def test_get_user_not_found(self, client):
        with patch('routes.users.execute_query', return_value=None):
            r = client.get('/api/users/999', headers=librarian_header())
        assert r.status_code == 404

    def test_update_user_profile(self, client):
        updated = {**self.FAKE_USER, 'name': 'Alice M. Johnson'}
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [None, updated]   # email uniqueness check, then SELECT
            r = client.put('/api/users/1',
                           headers=auth_header(user_id=1),
                           json={'name': 'Alice M. Johnson'})
        assert r.status_code == 200
        assert r.get_json()['user']['name'] == 'Alice M. Johnson'

    def test_update_user_forbidden(self, client):
        r = client.put('/api/users/2', headers=auth_header(user_id=1), json={'name': 'Hacker'})
        assert r.status_code == 403

    def test_update_user_no_fields(self, client):
        r = client.put('/api/users/1', headers=auth_header(user_id=1), json={})
        assert r.status_code == 400

    def test_list_users_librarian(self, client):
        with patch('routes.users.execute_query', return_value=[self.FAKE_USER]):
            r = client.get('/api/users', headers=librarian_header())
        assert r.status_code == 200
        assert r.get_json()['count'] == 1

    def test_list_users_forbidden_for_student(self, client):
        r = client.get('/api/users', headers=auth_header())
        assert r.status_code == 403

    def test_list_users_invalid_pagination(self, client):
        r = client.get('/api/users?limit=bad', headers=librarian_header())
        assert r.status_code == 400

    def test_change_user_role_admin(self, client):
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [{'user_id': 1, 'role': 'student'}, None]
            r = client.put('/api/users/1/role',
                           headers=admin_header(),
                           json={'role': 'librarian'})
        assert r.status_code == 200
        assert r.get_json()['new_role'] == 'librarian'

    def test_change_user_role_invalid(self, client):
        r = client.put('/api/users/1/role', headers=admin_header(), json={'role': 'superuser'})
        assert r.status_code == 400

    def test_change_user_role_forbidden_for_librarian(self, client):
        r = client.put('/api/users/1/role', headers=librarian_header(), json={'role': 'admin'})
        assert r.status_code == 403

    def test_get_user_activity(self, client):
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, [], [], [], []]
            r = client.get('/api/users/1/activity', headers=librarian_header())
        assert r.status_code == 200
        data = r.get_json()
        assert 'recent_loans' in data
        assert 'recent_fines' in data
        assert 'active_reservations' in data
        assert 'reading_list' in data

    def test_get_user_activity_forbidden_for_student(self, client):
        r = client.get('/api/users/1/activity', headers=auth_header())
        assert r.status_code == 403

    def test_delete_user_admin(self, client):
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, {'count': 0}, None]
            r = client.delete('/api/users/1', headers=admin_header())
        assert r.status_code == 200

    def test_delete_user_with_active_loans(self, client):
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, {'count': 2}]
            r = client.delete('/api/users/1', headers=admin_header())
        assert r.status_code == 400
        assert 'active loans' in r.get_json()['error']

    def test_delete_user_forbidden_for_librarian(self, client):
        r = client.delete('/api/users/1', headers=librarian_header())
        assert r.status_code == 403

    def test_get_user_stats_admin(self, client):
        fake_stats = {
            'total_users': 100, 'students': 80, 'faculty': 15,
            'librarians': 4, 'admins': 1, 'users_with_fines': 10,
            'total_outstanding_fines': 50.00
        }
        with patch('routes.users.execute_query') as mock_q:
            mock_q.side_effect = [fake_stats, {'count': 5}, {'count': 20}]
            r = client.get('/api/users/stats', headers=admin_header())
        assert r.status_code == 200
        assert r.get_json()['total_users'] == 100

    def test_get_users_with_fines_librarian(self, client):
        with patch('routes.users.execute_query', return_value=[
            {'user_id': 1, 'name': 'Alice', 'email': 'alice@u.edu', 'total_owed': 5.00}
        ]):
            r = client.get('/api/users/with-fines', headers=librarian_header())
        assert r.status_code == 200
        assert r.get_json()['count'] == 1

    def test_get_user_loans(self, client):
        fake_loans = [
            {'loan_id': 1, 'checkout_date': '2026-03-01', 'due_date': '2026-03-15',
             'return_date': None, 'status': 'active', 'title': 'Clean Code',
             'author': 'R. Martin', 'ISBN': '978-X', 'days_overdue': -2}
        ]
        with patch('routes.users.execute_query', return_value=fake_loans):
            r = client.get('/api/users/1/loans', headers=auth_header(user_id=1))
        assert r.status_code == 200
        assert r.get_json()['count'] == 1

    def test_get_user_loans_forbidden(self, client):
        r = client.get('/api/users/2/loans', headers=auth_header(user_id=1))
        assert r.status_code == 403

    def test_get_user_loans_status_filter(self, client):
        """Active/overdue filter uses the ActiveLoans view — different response shape."""
        fake_loans = [
            {'loan_id': 1, 'name': 'Alice Johnson', 'email': 'alice@university.edu',
             'title': 'Clean Code', 'ISBN': '978-X',
             'checkout_date': '2026-03-01', 'due_date': '2026-04-01', 'days_overdue': -5}
        ]
        with patch('routes.users.execute_query', return_value=fake_loans):
            r = client.get('/api/users/1/loans?status=active', headers=auth_header(user_id=1))
        assert r.status_code == 200
        assert r.get_json()['count'] == 1

    def test_get_users_with_fines_forbidden_for_student(self, client):
        r = client.get('/api/users/with-fines', headers=auth_header())
        assert r.status_code == 403

    def test_get_my_profile_user_not_found(self, client):
        with patch('routes.users.execute_query', return_value=None):
            r = client.get('/api/users/me', headers=auth_header())
        assert r.status_code == 404

    def test_update_user_duplicate_email(self, client):
        with patch('routes.users.execute_query', return_value={'user_id': 99}):
            r = client.put('/api/users/1',
                           headers=auth_header(user_id=1),
                           json={'email': 'taken@university.edu'})
        assert r.status_code == 409

    def test_update_user_invalid_email(self, client):
        r = client.put('/api/users/1',
                       headers=auth_header(user_id=1),
                       json={'email': 'not-a-valid-email'})
        assert r.status_code == 400

    def test_list_users_search_filter(self, client):
        with patch('routes.users.execute_query', return_value=[]):
            r = client.get('/api/users?search=alice&role=student&has_fines=true',
                           headers=librarian_header())
        assert r.status_code == 200

    def test_change_role_user_not_found(self, client):
        with patch('routes.users.execute_query', return_value=None):
            r = client.put('/api/users/999/role',
                           headers=admin_header(),
                           json={'role': 'librarian'})
        assert r.status_code == 404

    def test_delete_user_not_found(self, client):
        with patch('routes.users.execute_query', return_value=None):
            r = client.delete('/api/users/999', headers=admin_header())
        assert r.status_code == 404


# ============================================================
# Additional edge-case tests
# ============================================================

class TestAuthEdgeCases:
    def test_invalid_token_format(self, client):
        """Token present but not 'Bearer <token>' format."""
        r = client.get('/api/users/me', headers={'Authorization': 'Token abc123'})
        assert r.status_code == 401

    def test_malformed_bearer_token(self, client):
        """Bearer prefix present but token is garbage."""
        r = client.get('/api/users/me', headers={'Authorization': 'Bearer not.a.real.token'})
        assert r.status_code == 401

    def test_register_no_letter_in_password(self, client):
        """Password with only digits fails the letter requirement."""
        r = client.post('/api/auth/register', json={
            'name': 'John', 'email': 'john@university.edu', 'password': '12345678'
        })
        assert r.status_code == 400

    def test_register_no_number_in_password(self, client):
        """Password with only letters fails the number requirement."""
        r = client.post('/api/auth/register', json={
            'name': 'John', 'email': 'john@university.edu', 'password': 'abcdefgh'
        })
        assert r.status_code == 400


class TestBooksEdgeCases:
    def test_add_book_zero_copies(self, client):
        r = client.post('/api/books', headers=librarian_header(), json={
            'bookIsbn': '978-0451524935', 'bookTitle': '1984',
            'bookAuthor': 'George Orwell', 'bookGenre': 'Fiction', 'bookCopies': 0
        })
        assert r.status_code == 400

    def test_add_book_non_integer_copies(self, client):
        r = client.post('/api/books', headers=librarian_header(), json={
            'bookIsbn': '978-0451524935', 'bookTitle': '1984',
            'bookAuthor': 'George Orwell', 'bookGenre': 'Fiction', 'bookCopies': 'three'
        })
        assert r.status_code == 400

    def test_search_by_genre_filter(self, client):
        with patch('routes.books.execute_query', return_value=[]):
            r = client.get('/api/books?genre=Technology')
        assert r.status_code == 200

    def test_search_available_filter(self, client):
        with patch('routes.books.execute_query', return_value=[]):
            r = client.get('/api/books?available=true')
        assert r.status_code == 200


class TestLoansEdgeCases:
    FAKE_LOAN = {
        'loan_id': 1, 'user_id': 1, 'book_id': 1,
        'due_date': date.today() + timedelta(days=5),
        'status': 'active', 'title': 'Clean Code'
    }

    def test_checkout_requires_auth(self, client):
        r = client.post('/api/loans/checkout', json={'book_id': 1})
        assert r.status_code == 401

    def test_return_librarian_can_return_others_loan(self, client):
        """Librarian should be able to return a loan belonging to another user."""
        other_loan = {**self.FAKE_LOAN, 'user_id': 99}
        with patch('routes.loans.execute_query') as mock_q:
            mock_q.side_effect = [other_loan, None, None]
            r = client.post('/api/loans/1/return', headers=librarian_header())
        assert r.status_code == 200

    def test_renew_not_your_loan_student(self, client):
        """Student cannot renew a loan belonging to someone else."""
        other_loan = {**self.FAKE_LOAN, 'user_id': 99}
        with patch('routes.loans.execute_query', return_value=other_loan):
            r = client.post('/api/loans/1/renew', headers=auth_header(user_id=1))
        assert r.status_code == 403

    def test_renew_librarian_can_renew_others(self, client):
        """Librarian should be able to renew any loan."""
        other_loan = {**self.FAKE_LOAN, 'user_id': 99}
        with patch('routes.loans.execute_query') as mock_q:
            mock_q.side_effect = [other_loan, None]
            r = client.post('/api/loans/1/renew', headers=librarian_header())
        assert r.status_code == 200

    def test_get_overdue_loans_forbidden_for_student(self, client):
        r = client.get('/api/loans/overdue', headers=auth_header())
        assert r.status_code == 403


class TestReservationsEdgeCases:
    def test_create_reservation_requires_auth(self, client):
        r = client.post('/api/reservations', json={'book_id': 1})
        assert r.status_code == 401

    def test_get_user_reservations_not_found(self, client):
        with patch('routes.reservations.execute_query') as mock_q:
            mock_q.side_effect = [None]   # user lookup returns nothing → 404
            r = client.get('/api/reservations/user/999', headers=librarian_header())
        assert r.status_code == 404

    def test_cancel_not_your_reservation(self, client):
        other_reservation = {'reservation_id': 1, 'user_id': 99, 'book_id': 2, 'status': 'pending'}
        with patch('routes.reservations.execute_query', return_value=other_reservation):
            r = client.put('/api/reservations/1/cancel', headers=auth_header(user_id=1))
        assert r.status_code == 403

    def test_get_book_queue_not_found(self, client):
        with patch('routes.reservations.execute_query', return_value=None):
            r = client.get('/api/reservations/book/999', headers=auth_header())
        assert r.status_code == 404


class TestFinesEdgeCases:
    FAKE_USER = {'user_id': 1, 'name': 'Alice', 'fine_balance': 4.00}
    FAKE_FINE = {'fine_id': 1, 'user_id': 1, 'amount': 4.00, 'paid_status': 'unpaid'}

    def test_get_fines_with_status_filter(self, client):
        with patch('routes.fines.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, [self.FAKE_FINE]]
            r = client.get('/api/fines/user/1?status=unpaid', headers=auth_header())
        assert r.status_code == 200
        assert r.get_json()['count'] == 1

    def test_librarian_can_view_others_fines(self, client):
        """Librarian should be able to view any user's fines."""
        with patch('routes.fines.execute_query') as mock_q:
            mock_q.side_effect = [self.FAKE_USER, []]
            r = client.get('/api/fines/user/1', headers=librarian_header())
        assert r.status_code == 200

    def test_waive_fine_not_found(self, client):
        with patch('routes.fines.execute_query', return_value=None):
            r = client.post('/api/fines/999/waive', headers=librarian_header())
        assert r.status_code == 404
