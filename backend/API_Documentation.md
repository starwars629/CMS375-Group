# Library Management System - API Documentation

**Base URL:** `http://localhost:5000`  
**Version:** 1.0  
**Authors:** Andrew, Ethan, Mauricio

---

## Table of Contents

1. [Authentication](#authentication)
2. [Books](#books)
3. [Loans](#loans)
4. [Reservations](#reservations)
5. [Fines](#fines)
6. [Users](#users)
7. [Error Codes](#error-codes)

---

## Authentication

Most endpoints require authentication via JWT token:
```
Authorization: Bearer {token}
```

### Register

**POST** '/api/auth/register

Create a new user account.

**Request**
```json
{
  "name": "John Doe",
  "email": "John@example.com",
  "password": "SecurePass123"
}
```

**Success Response (201):**
```json
{
  "message": "User created successfully",
  "user_id": 42
}
```

**Error Responses:**

**400 - Validation Error:**
```json
{
  "error": "| Email is required| Password is required"
}
```
```json
{
  "error": "Invalid email format"
}
```
```json
{
  "error": "Password must be at least 8 characters"
}
```

**409 - Conflict:**
```json
{
  "error": "Email already registered"
}
```

**500 - Server Error:**
```json
{
  "error": "Registration failed"
}
```

---

### Login

**POST** '/api/auth/login

Authenticates user and receive JWT token.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student",
    "fine_balance": 0.00,
    "created_at": "2026-03-25T10:30:00"
  }
}
```

**Error Responses:**

**400 - Missing Fields:**
```json
{
  "error": "Email and password required"
}
```

**401 - Invalid Credentials:**
```json
{
  "error": "Invalid credentials"
}
```

---

### Logout

**POST** '/api/auth/logout

🔒 **Requires:** Authentication

Logout current user (client should delete token).

**Headers:**
```
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Error Responses:**

**401 - Not Authenticated:**
```json
{
  "error": "No authentication token provided"
}
```

---

### Change Password

**POST** '/api/auth/change-password

🔒 **Requires:** authentication

Change current user's password.

**Headers:**
```
Authorization: Bearer {token}
```

**Request:**
```json
{
  "current_password": "oldPass123"
  "new_password": "newSecurePass456"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**

**400 - Missing Fields:**
```json
{
  "error": "Current and new password required"
}
```

**400 - Weak Password:**
```json
{
  "error": "Password must be at least 8 characters"
}
```

**401 - Wrong Current Password:**
```json
{
  "error": "Current password is incorrect"
}
```

---

## Books

### List Books

**GET** `/api/books`

Get a list of all books with optional search and filters.

**Authentication:** not required

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | No | Search term for title, author, or ISBN |
| genre | string | No | Filter by genre |
| available | boolean | No | Filter by availability (true/false) |
| limit | integer | No | Max results (default: 50) |
| offset | integer | No | Skip first N results (default: 0) |

**Example Requests:**
```bash
# Get all books
GET /api/books

# Search for books
GET /api/books?query=harry+potter

# Filter by genre
GET /api/books?genre=Fantasy

# Available books only
GET /api/books?available=true

# Combined filters with pagination
GET /api/books?query=database&genre=Technology&limit=10&offset=0
```

**Success Response (200):**
```json
{
  "books": [
    {
      "book_id": 1,
      "ISBN": "978-0132350884",
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "genre": "Technology",
      "subject": "Software Engineering",
      "total_copies": 3,
      "available_copies": 3,
      "location": "Section A - Shelf 2",
      "created_at": "2026-03-25T10:30:00"
    },
    {
      "book_id": 2,
      "ISBN": "978-0201633610",
      "title": "Design Patterns",
      "author": "Gang of Four",
      "genre": "Technology",
      "subject": "Software Engineering",
      "total_copies": 2,
      "available_copies": 1,
      "location": "Section A - Shelf 3",
      "created_at": "2026-03-25T10:31:00"
    }
  ],
  "count": 2,
  "limit": 50,
  "offset": 0
}
```

**Error Responses:**

**500 - Server Error:**
```json
{
  "error": "Failed to fetch books"
}
```

---

### Get Single Book

**GET** `/api/books/{book_id}`

Get detailed information about a specific book.

**Authentication:** Not required

**URL Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| book_id | integer | Yes | The ID of the book |

**Example Request:**
```bash
GET /api/books/1
```

**Success Response (200):**
```json
{
  "book_id": 1,
  "ISBN": "978-0132350884",
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Technology",
  "subject": "Software Engineering",
  "total_copies": 3,
  "available_copies": 3,
  "location": "Section A - Shelf 2",
  "created_at": "2026-03-25T10:30:00"
}
```

**Error Responses:**

**404 - Book Not Found:**
```json
{
  "error": "Book not found"
}
```

**500 - Server Error:**
```json
{
  "error": "Failed to fetch book"
}
```
---

### Add Book

**POST** `/api/books`

🔒 **Requires:** Librarian authentication

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "bookIsbn": "978-0451524935",
  "bookTitle": "1984",
  "bookAuthor": "George Orwell",
  "bookGenre": "Fiction",
  "bookYear": 1949,
  "bookCopies": 5
}
```

**Required Fields:**
- `bookIsbn` (string) - ISBN number (10 or 13 digits)
- `bookTitle` (string) - Book title
- `bookAuthor` (string) - Book author
- `bookGenre` (string) - Book genre
- `bookYear` (integer) - Publication year
- `bookCopies` (integer) - Number of copies (minimum 1)

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGc..." \
  -d '{
    "bookIsbn": "978-0451524935",
    "bookTitle": "1984",
    "bookAuthor": "George Orwell",
    "bookGenre": "Fiction",
    "bookYear": 1949,
    "bookCopies": 5
  }'
```

**Success Response (201):**
```json
{
  "message": "Book added successfully",
  "book_id": 42
}
```

**Error Responses:**

**400 - Validation Error:**
```json
{
  "error": "| ISBN is required| Title is required"
}
```
```json
{
  "error": "Invalid ISBN format. Must be 10 or 13 digits"
}
```
```json
{
  "error": "Total copies must be at least 1"
}
```

**401 - Not Authenticated:**
```json
{
  "error": "No authentication token provided"
}
```

**403 - Insufficient Permissions:**
```json
{
  "error": "Access denied. Required roles: librarian",
  "your_role": "student"
}
```

**409 - Conflict (Duplicate ISBN):**
```json
{
  "error": "Book with this ISBN already exists"
}
```

**500 - Server Error:**
```json
{
  "error": "Database error occurred"
}
```

---

## Loans

### Checkout Book

**POST** `/api/loans/checkout`

🔒 **Requires:** Authentication

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "book_id": 1
}
```

**Loan Periods by Role:**
| Role | Loan Period |
|------|-------------|
| Student | 14 days |
| Faculty | 30 days |
| Librarian | 30 days |
| Admin | 30 days |

**Success Response (201):**
```json
{
  "message": "Book checked out successfully",
  "loan_id": 1,
  "book_id": 1,
  "title": "Clean Code",
  "checkout_date": "2026-04-13",
  "due_date": "2026-04-27"
}
```

**Error Responses:**

**400 - Missing Field:**
```json
{ "error": "book_id is required" }
```

**400 - No Copies Available:**
```json
{ "error": "No copies available" }
```

**400 - Already Borrowed:**
```json
{ "error": "You already have this book checked out" }
```

**404 - Book Not Found:**
```json
{ "error": "Book not found" }
```

**500 - Server Error:**
```json
{ "error": "Checkout failed" }
```

---

### Return Book

**POST** `/api/loans/{loan_id}/return`

🔒 **Requires:** Authentication (users can only return their own loans unless librarian/admin)

If the book is returned late, a fine of **$1.00/day** is automatically generated and added to the user's account.

**Headers:**
```
Authorization: Bearer {token}
```

**Success Response (200) — On time:**
```json
{
  "message": "Book returned successfully",
  "loan_id": 1,
  "title": "Clean Code",
  "return_date": "2026-04-27"
}
```

**Success Response (200) — Overdue:**
```json
{
  "message": "Book returned successfully",
  "loan_id": 1,
  "title": "Clean Code",
  "return_date": "2026-05-01",
  "fine": {
    "fine_id": 3,
    "days_overdue": 4,
    "amount": 4.00,
    "message": "A fine of $4.00 has been added to your account"
  }
}
```

**Error Responses:**

**400 - Not Active:**
```json
{ "error": "This loan is not active" }
```

**403 - Forbidden:**
```json
{ "error": "You can only return your own loans" }
```

**404 - Not Found:**
```json
{ "error": "Loan not found" }
```

**500 - Server Error:**
```json
{ "error": "Return failed" }
```

---

### Renew Loan

**POST** `/api/loans/{loan_id}/renew`

🔒 **Requires:** Authentication (users can only renew their own loans unless librarian/admin)

Extends the due date by the user's full loan period from the current due date. Overdue loans cannot be renewed.

**Headers:**
```
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "message": "Loan renewed successfully",
  "loan_id": 1,
  "title": "Clean Code",
  "old_due_date": "2026-04-27",
  "new_due_date": "2026-05-11"
}
```

**Error Responses:**

**400 - Not Active:**
```json
{ "error": "Only active loans can be renewed" }
```

**400 - Overdue:**
```json
{ "error": "Overdue loans cannot be renewed. Please return the book and pay the fine." }
```

**403 - Forbidden:**
```json
{ "error": "You can only renew your own loans" }
```

**404 - Not Found:**
```json
{ "error": "Loan not found" }
```

**500 - Server Error:**
```json
{ "error": "Renewal failed" }
```

---

### Get Active Loans

**GET** `/api/loans/active`

🔒 **Requires:** Librarian or Admin authentication

Returns all loans with status `active` or `overdue`.

**Headers:**
```
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "loans": [
    {
      "loan_id": 1,
      "checkout_date": "2026-04-01",
      "due_date": "2026-04-15",
      "status": "active",
      "user_id": 3,
      "borrower_name": "Alice Johnson",
      "borrower_email": "alice@university.edu",
      "book_id": 1,
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "ISBN": "978-0132350884",
      "days_overdue": -2
    }
  ],
  "count": 1
}
```

**Error Responses:**

**403 - Forbidden:**
```json
{ "error": "Access denied. Required roles: librarian or admin" }
```

**500 - Server Error:**
```json
{ "error": "Failed to fetch active loans" }
```

---

### Get Overdue Loans

**GET** `/api/loans/overdue`

🔒 **Requires:** Librarian or Admin authentication

Returns all loans that are past their due date, along with days overdue and the accrued fine amount.

**Headers:**
```
Authorization: Bearer {token}
```

**Success Response (200):**
```json
{
  "loans": [
    {
      "loan_id": 2,
      "checkout_date": "2026-03-10",
      "due_date": "2026-03-24",
      "user_id": 5,
      "borrower_name": "Bob Smith",
      "borrower_email": "bob@university.edu",
      "book_id": 2,
      "title": "Design Patterns",
      "author": "Gang of Four",
      "ISBN": "978-0201633610",
      "days_overdue": 20,
      "accrued_fine": 20.00
    }
  ],
  "count": 1
}
```

**Error Responses:**

**403 - Forbidden:**
```json
{ "error": "Access denied. Required roles: librarian or admin" }
```

**500 - Server Error:**
```json
{ "error": "Failed to fetch overdue loans" }
```

---

## Reservations

**Status:** To Be Implemented

Planned endpoints:
- `POST /api/reservations` - Create a reservation
- `GET /api/reservations/user/{user_id}` - Get user's reservations
- `PUT /api/reservations/{reservation_id}/cancel` - Cancel a reservation
- `GET /api/reservations/book/{book_id}` - Get reservation queue for a book

---

## Fines

**Status:** To Be Implemented

Planned endpoints:
- `GET /api/fines/user/{user_id}` - Get user's fines
- `POST /api/fines/{fine_id}/pay` - Pay a fine
- `POST /api/fines/{fine_id}/waive` - Waive a fine (Librarian only)
- `GET /api/fines/outstanding` - Get all outstanding fines

---

## Users

### Get My Profile

**GET** `/api/users/me`

Get current authenticated user's profile with statistics.

🔒 **Requires:** Authentication

**Headers:**
```
Authorization: Bearer {token}
```

**Example Request:**
```bash
curl http://localhost:5000/api/users/me \
  -H "Authorization: Bearer eyJhbGc..."
```

**Success Response (200):**
```json
{
  "user_id": 1,
  "name": "Alice Johnson",
  "email": "alice@university.edu",
  "role": "student",
  "fine_balance": 5.50,
  "created_at": "2026-01-15T08:00:00",
  "stats": {
    "total_books_borrowed": 15,
    "currently_borrowed": 2,
    "overdue_books": 1,
    "pending_reservations": 1
  }
}
```

**Error Responses:**

**401 - Not Authenticated:**
```json
{
  "error": "No authentication token provided"
}
```

**404 - User Not Found:**
```json
{
  "error": "User not found"
}
```

---

### Get User Profile

**GET** `/api/users/{user_id}`

Get user profile information.

🔒 **Requires:** Authentication (users can only view own profile unless librarian/admin)

**Headers:**
```
Authorization: Bearer {token}
```

**URL Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | The ID of the user |

**Example Request:**
```bash
curl http://localhost:5000/api/users/1 \
  -H "Authorization: Bearer eyJhbGc..."
```

**Success Response (200):**
```json
{
  "user_id": 1,
  "name": "Alice Johnson",
  "email": "alice@university.edu",
  "role": "student",
  "fine_balance": 5.50,
  "created_at": "2026-01-15T08:00:00",
  "stats": {
    "total_books_borrowed": 15,
    "currently_borrowed": 2,
    "overdue_books": 1,
    "pending_reservations": 1
  }
}
```

**Error Responses:**

**403 - Forbidden:**
```json
{
  "error": "You can only view your own profile"
}
```

**404 - User Not Found:**
```json
{
  "error": "User not found"
}
```

---

### Update User Profile

**PUT** `/api/users/{user_id}`

Update user profile information.

🔒 **Requires:** Authentication (users can only update own profile)

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Alice Marie Johnson",
  "email": "alice.johnson@university.edu"
}
```

**Optional Fields:**
- `name` (string) - User's full name
- `email` (string) - User's email address

**Example Request:**
```bash
curl -X PUT http://localhost:5000/api/users/1 \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Marie Johnson",
    "email": "alice.johnson@university.edu"
  }'
```

**Success Response (200):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "user_id": 1,
    "name": "Alice Marie Johnson",
    "email": "alice.johnson@university.edu",
    "role": "student",
    "fine_balance": 5.50
  }
}
```

**Error Responses:**

**400 - Validation Error:**
```json
{
  "error": "Invalid email format"
}
```
```json
{
  "error": "No fields to update"
}
```

**403 - Forbidden:**
```json
{
  "error": "You can only update your own profile"
}
```

**409 - Conflict:**
```json
{
  "error": "Email already in use"
}
```

**500 - Server Error:**
```json
{
  "error": "Update failed"
}
```

---

### List All Users

**GET** `/api/users`

Get a list of all users with optional filters (Librarian/Admin only).

🔒 **Requires:** Librarian or Admin authentication

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| search | string | No | Search by name or email |
| role | string | No | Filter by role (student, faculty, librarian, admin) |
| has_fines | boolean | No | Filter users with fines (true/false) |
| limit | integer | No | Max results (default: 50) |
| offset | integer | No | Skip results (default: 0) |

**Example Requests:**
```bash
# Get all users
GET /api/users

# Search for users
GET /api/users?search=alice

# Filter by role
GET /api/users?role=student

# Users with fines
GET /api/users?has_fines=true

# Combined filters
GET /api/users?search=john&role=faculty&limit=20
```

**Success Response (200):**
```json
{
  "users": [
    {
      "user_id": 1,
      "name": "Alice Johnson",
      "email": "alice@university.edu",
      "role": "student",
      "fine_balance": 5.50,
      "created_at": "2026-01-15T08:00:00",
      "active_loans": 2,
      "overdue_books": 1
    },
    {
      "user_id": 2,
      "name": "Bob Smith",
      "email": "bob@university.edu",
      "role": "faculty",
      "fine_balance": 0.00,
      "created_at": "2026-01-20T09:00:00",
      "active_loans": 3,
      "overdue_books": 0
    }
  ],
  "count": 2,
  "limit": 50,
  "offset": 0
}
```

**Error Responses:**

**403 - Forbidden:**
```json
{
  "error": "Access denied. Required roles: librarian or admin",
  "your_role": "student"
}
```

**500 - Server Error:**
```json
{
  "error": "Failed to fetch users"
}
```

---

### Change User Role

**PUT** `/api/users/{user_id}/role`

Change a user's role (Admin only).

🔒 **Requires:** Admin authentication

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "role": "librarian"
}
```

**Valid Roles:**
- `student`
- `faculty`
- `librarian`
- `admin`

**Example Request:**
```bash
curl -X PUT http://localhost:5000/api/users/1/role \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "role": "librarian"
  }'
```

**Success Response (200):**
```json
{
  "message": "User role updated successfully",
  "user_id": 1,
  "old_role": "student",
  "new_role": "librarian"
}
```

**Error Responses:**

**400 - Validation Error:**
```json
{
  "error": "Role is required"
}
```
```json
{
  "error": "Invalid role. Must be one of: student, faculty, librarian, admin"
}
```

**403 - Forbidden:**
```json
{
  "error": "Access denied. Required roles: admin",
  "your_role": "librarian"
}
```

**404 - User Not Found:**
```json
{
  "error": "User not found"
}
```

---

### Get User Activity

**GET** `/api/users/{user_id}/activity`

Get user's complete activity history (Librarian/Admin only).

🔒 **Requires:** Librarian or Admin authentication

**Headers:**
```
Authorization: Bearer {token}
```

**Example Request:**
```bash
curl http://localhost:5000/api/users/1/activity \
  -H "Authorization: Bearer eyJhbGc..."
```

**Success Response (200):**
```json
{
  "user": {
    "user_id": 1,
    "name": "Alice Johnson",
    "email": "alice@university.edu"
  },
  "recent_loans": [
    {
      "loan_id": 5,
      "checkout_date": "2026-03-20",
      "due_date": "2026-04-03",
      "return_date": null,
      "status": "active",
      "book_title": "Clean Code",
      "book_author": "Robert C. Martin",
      "ISBN": "978-0132350884"
    }
  ],
  "recent_fines": [
    {
      "fine_id": 2,
      "amount": 2.50,
      "issued_at": "2026-03-15T10:00:00",
      "paid_at": null,
      "paid_status": "unpaid",
      "book_title": "Design Patterns",
      "book_author": "Gang of Four"
    }
  ],
  "active_reservations": [
    {
      "reservation_id": 3,
      "reservation_date": "2026-03-22T14:30:00",
      "status": "pending",
      "book_title": "The C Programming Language",
      "book_author": "Kernighan & Ritchie",
      "ISBN": "978-0131103627"
    }
  ],
  "reading_list": [
    {
      "list_id": 1,
      "added_at": "2026-03-10T12:00:00",
      "book_id": 4,
      "title": "Database Design for Mere Mortals",
      "author": "M.J. Hernandez",
      "ISBN": "978-0132130806"
    }
  ]
}
```

**Error Responses:**

**403 - Forbidden:**
```json
{
  "error": "Access denied. Required roles: librarian or admin"
}
```

**404 - User Not Found:**
```json
{
  "error": "User not found"
}
```

---

### Delete User

**DELETE** `/api/users/{user_id}`

Delete a user account (Admin only).

🔒 **Requires:** Admin authentication

**Headers:**
```
Authorization: Bearer {token}
```

**Example Request:**
```bash
curl -X DELETE http://localhost:5000/api/users/1 \
  -H "Authorization: Bearer eyJhbGc..."
```

**Success Response (200):**
```json
{
  "message": "User deleted successfully",
  "user_id": 1,
  "name": "Alice Johnson"
}
```

**Error Responses:**

**400 - Cannot Delete:**
```json
{
  "error": "Cannot delete user with active loans",
  "active_loans": 2
}
```

**403 - Forbidden:**
```json
{
  "error": "Access denied. Required roles: admin"
}
```

**404 - User Not Found:**
```json
{
  "error": "User not found"
}
```

---

### Get User Statistics

**GET** `/api/users/stats`

Get overall user statistics (Admin only).

🔒 **Requires:** Admin authentication

**Headers:**
```
Authorization: Bearer {token}
```

**Example Request:**
```bash
curl http://localhost:5000/api/users/stats \
  -H "Authorization: Bearer eyJhbGc..."
```

**Success Response (200):**
```json
{
  "total_users": 125,
  "students": 98,
  "faculty": 20,
  "librarians": 5,
  "admins": 2,
  "users_with_fines": 15,
  "total_outstanding_fines": 347.50,
  "users_with_overdue": 12,
  "active_borrowers": 45
}
```

**Error Responses:**

**403 - Forbidden:**
```json
{
  "error": "Access denied. Required roles: admin"
}
```

---

### Get Users with Fines

**GET** `/api/users/with-fines`

Get all users with unpaid fines (Librarian/Admin only).

🔒 **Requires:** Librarian or Admin authentication

**Headers:**
```
Authorization: Bearer {token}
```

**Example Request:**
```bash
curl http://localhost:5000/api/users/with-fines \
  -H "Authorization: Bearer eyJhbGc..."
```

**Success Response (200):**
```json
{
  "users": [
    {
      "user_id": 1,
      "name": "Alice Johnson",
      "email": "alice@university.edu",
      "total_owed": 15.50
    },
    {
      "user_id": 5,
      "name": "Charlie Brown",
      "email": "charlie@university.edu",
      "total_owed": 8.00
    }
  ],
  "count": 2
}
```

**Error Responses:**

**403 - Forbidden:**
```json
{
  "error": "Access denied. Required roles: librarian or admin"
}
```

---

### Get User's Loans

**GET** `/api/users/{user_id}/loans`

Get user's loan history with optional status filter.

🔒 **Requires:** Authentication (users can only view own loans unless librarian/admin)

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status (active, returned, overdue) |

**Example Requests:**
```bash
# Get all loans
GET /api/users/1/loans

# Get active loans only
GET /api/users/1/loans?status=active

# Get overdue loans only
GET /api/users/1/loans?status=overdue
```

**Success Response (200):**
```json
{
  "loans": [
    {
      "loan_id": 1,
      "checkout_date": "2026-03-25",
      "due_date": "2026-04-08",
      "return_date": null,
      "status": "active",
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "ISBN": "978-0132350884",
      "days_overdue": -14
    },
    {
      "loan_id": 2,
      "checkout_date": "2026-03-10",
      "due_date": "2026-03-24",
      "return_date": null,
      "status": "overdue",
      "title": "Design Patterns",
      "author": "Gang of Four",
      "ISBN": "978-0201633610",
      "days_overdue": 18
    }
  ],
  "count": 2
}
```

**Error Responses:**

**403 - Forbidden:**
```json
{
  "error": "You can only view your own loans"
}
```

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or validation error |
| 401 | Unauthorized | Authentication required or invalid token |
| 403 | Forbidden | Insufficient permissions for this action |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g., ISBN or email already exists) |
| 500 | Internal Server Error | Something went wrong on server |

---

## Rate Limits

No rate limits currently implemented.

---

## Testing Examples

### Complete Workflow: Register, Login, Add Book

```bash
# 1. Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Librarian",
    "email": "testlib@university.edu",
    "password": "SecurePass123"
  }'

# Response: {"message": "User created successfully", "user_id": 5}

# 2. Login as admin to change role
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "david@university.edu",
    "password": "hashed_pw_4"
  }'

# Response: {"token": "eyJ...", "user": {...}}
# Save admin token: TOKEN_ADMIN="eyJ..."

# 3. Change new user's role to librarian
curl -X PUT http://localhost:5000/api/users/5/role \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"role": "librarian"}'

# 4. Login as the new librarian
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testlib@university.edu",
    "password": "SecurePass123"
  }'

# Save librarian token: TOKEN="eyJ..."

# 5. Add a book
curl -X POST http://localhost:5000/api/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bookIsbn": "978-0596009205",
    "bookTitle": "Head First Design Patterns",
    "bookAuthor": "Eric Freeman",
    "bookGenre": "Technology",
    "bookYear": 2004,
    "bookCopies": 4
  }'

# Response: {"message": "Book added successfully", "book_id": 5}

# 6. Search for the book
curl "http://localhost:5000/api/books?query=head+first"

# 7. Get my profile
curl http://localhost:5000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Contact

For questions or issues, contact the development team:
- **Andrew:** Backend Developer
- **Ethan:** Frontend Developer
- **Mauricio:** Database Designer

**GitHub Repository:** [https://github.com/starwars629/CMS375-Group]

**Last Updated:** April 11, 2026