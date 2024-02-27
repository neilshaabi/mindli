import re

from wtforms.validators import ValidationError


def isValidEmail(email: str) -> bool:
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return email and re.match(email_regex, email)


def isValidPassword(password: str) -> bool:
    return (
        password
        and len(password) >= 8
        and any(char.isdigit() for char in password)
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
    )


def isValidText(text: str) -> bool:
    return text and not text.isspace()


class PasswordValidator:
    def __call__(self, form, field):
        password: str = field.data
        error: str = None

        if len(password) < 8:
            error = "Password must be at least 8 characters long."

        elif not any(char.isdigit() for char in password):
            error = "Password must include at least one digit."

        elif not any(char.isupper() for char in password):
            error = "Password must include at least one uppercase letter."

        elif not any(char.islower() for char in password):
            error = "Password must include at least one lowercase letter."

        if error:
            raise ValidationError(error)

        return
