import re

from werkzeug.security import check_password_hash
from wtforms.validators import ValidationError

from app import db
from app.models.user import User


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
            error = "Password must be at least 8 characters long"

        elif not any(char.isdigit() for char in password):
            error = "Password must include at least one digit"

        elif not any(char.isupper() for char in password):
            error = "Password must include at least one uppercase letter"

        elif not any(char.islower() for char in password):
            error = "Password must include at least one lowercase letter"

        if error:
            raise ValidationError(error)

        return


class UserCredentialsValidator:
    def __call__(self, form, field):
        email = form.email.data.lower()

        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if not user or not check_password_hash(user.password_hash, form.password.data):
            raise ValidationError("Incorrect email or password.")

        return
