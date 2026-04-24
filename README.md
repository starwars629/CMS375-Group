# CMS375-Group

Ethan - frontend
Andrew - backend
Mauricio - database

## Security and Database Notes

- Passwords are hashed with `bcrypt` in backend auth flows (`register` and `change-password`) and are never stored as plaintext.
- Backend SQL calls use parameterized placeholders (`%s`) through `execute_query`, and user profile updates now use fixed SQL templates instead of dynamic SQL fragments.
- Backend text inputs are sanitized before persistence to reduce stored XSS risk (for example, user name/email and book metadata fields).
- Frontend table actions escape user-controlled values before writing dynamic HTML/inline handlers.

### 3NF / Key / Constraint Review

- Tables use primary keys on each entity (`Users`, `Books`, `Loans`, `Fines`, `Reservations`, `ReadingLists`).
- Relationships are enforced with foreign keys and `ON DELETE` behavior, preventing orphan records.
- Constraints now include:
  - copy count consistency (`available_copies <= total_copies`)
  - non-negative fine amounts
  - one fine per loan (`UNIQUE loan_id`) to prevent duplicate fine rows
- Supporting indexes were added on foreign-key and common filter columns to improve integrity checks and query performance.

Note: `Users.fine_balance` and `Users.total_fines_paid` are maintained as denormalized summary values for faster dashboard reads; source-of-truth detail remains in `Fines`.