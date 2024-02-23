def isValidPassword(password: str) -> bool:
    """
    Returns whether a given password meets the security requirements
    (at least 8 characters with at least one digit, one uppercase letter
    and one lowercase letter)"""
    if (
        (len(password) < 8)
        or (not any(char.isdigit() for char in password))
        or (not any(char.isupper() for char in password))
        or (not any(char.islower() for char in password))
    ):
        return False
    else:
        return True
