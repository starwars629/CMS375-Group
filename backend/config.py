# ============================================================
# Library Management System - Central Configuration
# ============================================================
# All tuneable values live here. Import from this module
# instead of hard-coding values in individual files.
# ============================================================

# ----------------------
# Database
# ----------------------
DB_HOST      = 'localhost'
DB_USER      = 'root'
DB_PASSWORD  = ''
DB_NAME      = 'libraryDB'
DB_POOL_SIZE = 5

# ----------------------
# Authentication / JWT
# ----------------------
# NOTE: Replace this with a strong random value before deploying.
SECRET_KEY             = 'this-is-a-very-secure-key-that-is-at-least-32-bytes-long'
TOKEN_EXPIRATION_HOURS = 24
VALID_ROLES            = ['student', 'faculty', 'librarian', 'admin']

# ----------------------
# Loan Rules
# ----------------------
# How many days each role may borrow a book
LOAN_PERIODS = {
    'student':   14,
    'faculty':   30,
    'librarian': 30,
    'admin':     30,
}

# Maximum number of times a single loan may be renewed
MAX_RENEWALS = 2

# Fine charged per overdue day (in dollars)
FINE_RATE_PER_DAY = 1.00

# ----------------------
# Reservation Rules
# ----------------------
# Maximum number of active (pending) reservations per role
RESERVATION_LIMITS = {
    'student':   1,
    'faculty':   3,
    'librarian': 3,
    'admin':     3,
}

# ----------------------
# Flask Server
# ----------------------
DEBUG = True
PORT  = 5000