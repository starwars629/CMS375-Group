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

### Register

**POST** '/api/auth/register

**Request**
```json
{
  "name": "John Doe",
  "email": "John@example.com",
  "password": "SecurePass123"
}
```

**Response (201):**
```json
{
  "message": "Account created successfully",
  "user_id": 42
}
```

**Errors:**
- `400` - Validation error
- `409` - Account already exists with credentials
- `500` - Database connection error

### Login

**POST** '/api/auth/login

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123
}
```

**Response (200):**
```json
{
  "token": $token,
  "user": user
}
```

**Response (401):**
```json
{
  "error": "Invalid credentials"
}
```
### Logout

**POST** '/api/auth/register

🔒 **Requires:** Authentication

**Example:**
```
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

### Change Password

**POST** '/api/auth/register

🔒 **Requires:** authentication

**Request:**
```
  "current_password": "oldPass123"
  "new_password": "newSecurePass456"
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Errors:**
- `400` - Data validation error
- `401` - Incorrect password

---

## Books

### List Books

**GET** `/api/books`

**Parameters:**
- `query` (string, optional) - Search term
- `genre` (string, optional) - Filter by genre
- `available` (boolean, optional) - Filter available books
- `limit` (integer, optional) - Max results (default: 50)

**Example:**
```
GET /api/books?query=harry&genre=Fantasy
```

**Response (200):**
```json
{
  "books": [
    {
      "book_id": 1,
      "title": "Harry Potter",
      "author": "J.K. Rowling",
      "available_copies": 3
    }
  ],
  "count": 1
}
```

---

### Get Single Book

**GET** `/api/books/{book_id}`

**Response (200):**
```json
{
  "book_id": 1,
  "ISBN": "9780439139595",
  "title": "Harry Potter",
  "author": "J.K. Rowling",
  "available_copies": 3
}
```

**Response (404):**
```json
{
  "error": "Book not found"
}
```

---

### Add Book

**POST** `/api/books`

🔒 **Requires:** Librarian authentication

**Request:**
```json
{
  "ISBN": "9780451524935",
  "title": "1984",
  "author": "George Orwell",
  "genre": "Fiction",
  "total_copies": 5
}
```

**Response (201):**
```json
{
  "message": "Book added successfully",
  "book_id": 42
}
```

**Errors:**
- `400` - Validation error
- `401` - Not authenticated
- `403` - Not a librarian
- `409` - ISBN already exists

---

## Loans

TBD

---

## Reservations

TBD

---

## Fines

TBD

---

## Users

TBD

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Success |
| 201 | Created | Resource created |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 500 | Server Error | Internal error |

---

## Rate Limits

No rate limits currently implemented.

---
