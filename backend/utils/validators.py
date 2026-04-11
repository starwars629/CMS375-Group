"""
Validation Utilities
==========================
Helper functions for validating user input
"""

import re

def validate_password_strength(password):
    """
    Validates that password meets minimum requirements
    
    args:
        password (str): password to be validated

    returns:
        tuple: (bool, str): (is_valid, error_message)

    requirements:
        8 character length
        1 letter
        1 number
    """

    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    
    if not any(c.isalpha() for c in password):
        return False, 'Password must contain at least 1 letter'
    
    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least 1 number'
    
    return True, ''

def validate_email(email):
    """
    Validates email format
    
    args:
        email (str): email to validate

    returns:
        bool: valid_email
    """

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_isbn(isbn):
    """
    Validates ISBN format (10 or 13 digits)
    
    args:
        isbn (str): ISBN to validate

    returns: 
        bool: valid_ISBN
    """

    clean = isbn.replace('-', '').replace(' ', '')
    
    return clean.isdigit() and len(clean) in [10, 13]

def validate_phone(phone):
    """
    Validate US phone number
    
    args:
        phone (str): phone number to validate

    returns:
        bool: valid_phone_number
    """

    clean = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')

    return clean.isdigit() and len(clean) == 10

if __name__ == '__main__':
    """Test Validators"""
    print('Testing Validators')

    # Test email
    print("\nEmail validation:")
    print(f"'user@example.com': {validate_email('user@example.com')}")
    print(f"'not an email @fail.com': {validate_email('not an email @fail.com')}")
    print(f"'invalid': {validate_email('invalid')}")
    
    # Test password
    print("\nPassword validation:")
    print(f"'abc': {validate_password_strength('abc')}")
    print(f"'InsecurePass': {validate_password_strength('InsecurePass')}")
    print(f"'SecurePass123': {validate_password_strength('SecurePass123')}")
    
    # Test ISBN
    print("\nISBN validation:")
    print(f"'978-0-143-12774-1': {validate_isbn('978-0-143-12774-1')}")
    print(f"'123 4 5 67 8 9 0': {validate_isbn('123 4 5 67 8 9 0')}")
    print(f"'123': {validate_isbn('123')}")