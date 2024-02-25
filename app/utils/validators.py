import re

def isValidText(text: str) -> bool:
    return text and not text.isspace()

def isValidEmail(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return email and re.match(email_regex, email)

def isValidPassword(password: str) -> bool:
    return (
        password
        and len(password) >= 8
        and any(char.isdigit() for char in password)
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
    )