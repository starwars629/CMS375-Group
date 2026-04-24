-- ============================================================
-- Library Management System - Database Schema
-- Team: Ethan, Andrew, Mauricio
-- ============================================================

-- ============================================================
-- USERS TABLE
-- Stores all system users (students, faculty, librarians, admins)
-- ============================================================
CREATE TABLE Users (
    user_id       INT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password      VARCHAR(255) NOT NULL,  -- store hashed passwords only
    role          ENUM('student', 'faculty', 'librarian', 'admin') NOT NULL DEFAULT 'student',
    fine_balance       DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_fines_paid   DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- BOOKS TABLE
-- Stores all books in the library catalog
-- ============================================================
CREATE TABLE Books (
    book_id          INT PRIMARY KEY AUTO_INCREMENT,
    ISBN             VARCHAR(20) NOT NULL UNIQUE,
    title            VARCHAR(255) NOT NULL,
    author           VARCHAR(150) NOT NULL,
    genre            VARCHAR(100),
    subject          VARCHAR(150),
    total_copies     INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    location         VARCHAR(100),  -- shelf/section in the library
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_copies CHECK (available_copies >= 0),
    CONSTRAINT chk_total   CHECK (total_copies >= 0),
    CONSTRAINT chk_available_not_exceed_total CHECK (available_copies <= total_copies)
);

-- ============================================================
-- LOANS TABLE
-- Tracks book checkouts and returns
-- ============================================================
CREATE TABLE Loans (
    loan_id        INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    book_id        INT NOT NULL,
    checkout_date  DATE NOT NULL DEFAULT (CURRENT_DATE),
    due_date       DATE NOT NULL,
    return_date    DATE DEFAULT NULL,  -- NULL = not yet returned
    status         ENUM('active', 'returned', 'overdue') NOT NULL DEFAULT 'active',
    renewal_count  INT NOT NULL DEFAULT 0,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE RESTRICT,
    INDEX idx_loans_user_id (user_id),
    INDEX idx_loans_book_id (book_id),
    INDEX idx_loans_status_due_date (status, due_date)
);

-- ============================================================
-- FINES TABLE
-- Tracks fines tied to overdue loans
-- ============================================================
CREATE TABLE Fines (
    fine_id     INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    loan_id     INT NOT NULL,
    amount      DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    paid_status ENUM('unpaid', 'paid', 'waived') NOT NULL DEFAULT 'unpaid',
    issued_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at     TIMESTAMP NULL DEFAULT NULL,

    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (loan_id) REFERENCES Loans(loan_id) ON DELETE CASCADE,
    CONSTRAINT chk_fine_amount_non_negative CHECK (amount >= 0),
    UNIQUE KEY uq_fines_loan_id (loan_id),
    INDEX idx_fines_user_status (user_id, paid_status)
);

-- ============================================================
-- RESERVATIONS TABLE
-- Handles holds placed on checked-out books
-- ============================================================
CREATE TABLE Reservations (
    reservation_id   INT PRIMARY KEY AUTO_INCREMENT,
    user_id          INT NOT NULL,
    book_id          INT NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status           ENUM('pending', 'ready', 'fulfilled', 'cancelled') NOT NULL DEFAULT 'pending',

    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    INDEX idx_reservations_book_status_date (book_id, status, reservation_date),
    INDEX idx_reservations_user_status (user_id, status)
);

-- ============================================================
-- READING LISTS TABLE
-- Allows students/faculty to save favorite books
-- ============================================================
CREATE TABLE ReadingLists (
    list_id    INT PRIMARY KEY AUTO_INCREMENT,
    user_id    INT NOT NULL,
    book_id    INT NOT NULL,
    added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (user_id, book_id),  -- prevent duplicate entries
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    INDEX idx_reading_lists_user (user_id),
    INDEX idx_reading_lists_book (book_id)
);

-- ============================================================
-- USEFUL VIEWS
-- ============================================================

-- Books currently checked out with borrower info
CREATE VIEW ActiveLoans AS
SELECT
    l.loan_id,
    u.name        AS borrower,
    u.email,
    b.title,
    b.ISBN,
    l.checkout_date,
    l.due_date,
    DATEDIFF(CURRENT_DATE, l.due_date) AS days_overdue
FROM Loans l
JOIN Users u ON l.user_id = u.user_id
JOIN Books b ON l.book_id = b.book_id
WHERE l.status IN ('active', 'overdue');

-- Unpaid fines per user
CREATE VIEW UnpaidFines AS
SELECT
    u.user_id,
    u.name,
    u.email,
    SUM(f.amount) AS total_owed
FROM Fines f
JOIN Users u ON f.user_id = u.user_id
WHERE f.paid_status = 'unpaid'
GROUP BY u.user_id, u.name, u.email;

-- Most borrowed books (for admin reports)
CREATE VIEW MostBorrowedBooks AS
SELECT
    b.book_id,
    b.title,
    b.author,
    COUNT(l.loan_id) AS times_borrowed
FROM Books b
LEFT JOIN Loans l ON b.book_id = l.book_id
GROUP BY b.book_id, b.title, b.author
ORDER BY times_borrowed DESC;

-- ============================================================
-- SAMPLE DATA
-- ============================================================

INSERT INTO Users (name, email, password, role) VALUES
('Alice Johnson',  'alice@university.edu',   '$2b$12$w6eVWW08R8vqi4L6yrx7z.JlPo2P6qkqA6vYw9oM2CwNJHf4Q9z9S', 'student'),
('Bob Smith',      'bob@university.edu',     '$2b$12$7dYHlk4m45X4v5uW7bJHxeV2x8B5/2zQykcGhXANeH3fYf3l5w9yi', 'faculty'),
('Carol White',    'carol@university.edu',   '$2b$12$Y9UQ8Hw0k2R7MpNQ3RrOdu9j9hYx6vQGQ8Rk6cB4bXhG9G4s6Y6Ty', 'librarian'),
('David Admin',    'david@university.edu',   '$2b$12$Q2nD9xCcW4nN8LrP5sV0NOPuK6V5qXrY4zM4w5Dg0rP2aXoB3n6mK', 'admin');

INSERT INTO Books (ISBN, title, author, genre, subject, total_copies, available_copies, location) VALUES
('978-0132350884', 'Clean Code',                   'Robert C. Martin', 'Technology', 'Software Engineering', 3, 3, 'Section A - Shelf 2'),
('978-0201633610', 'Design Patterns',              'Gang of Four',     'Technology', 'Software Engineering', 2, 1, 'Section A - Shelf 3'),
('978-0131103627', 'The C Programming Language',   'Kernighan & Ritchie', 'Technology', 'Programming',      2, 2, 'Section B - Shelf 1'),
('978-0132130806', 'Database Design for Mere Mortals', 'M.J. Hernandez', 'Technology', 'Database Design',  4, 4, 'Section B - Shelf 4');
