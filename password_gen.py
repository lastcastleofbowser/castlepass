from flask import session
import string
import secrets

def password_generator(length, uppercase, lowercase, numbers, symbols):
    """Generate a random password."""
    min_length = 6
    max_length = 25

    pass_length = session.get("pass_length")

    if pass_length < min_length or pass_length > max_length:
        raise ValueError(f"Password length must be between {min_length} and {max_length} characters long.")
    
    uppercase = bool(session.get("uppercase", True))
    lowercase = bool(session.get("lowercase", True))
    numbers = bool(session.get("numbers", True))
    symbols = bool(session.get("symbols", True))

    password = ''

    if uppercase:
        password += string.ascii_uppercase
    if lowercase:
        password += string.ascii_lowercase
    if numbers:
        password += string.digits
    if symbols:
        password += string.punctuation
        
    password = ''.join(secrets.choice(password) for i in range(pass_length))
    return password