from wtforms.validators import ValidationError


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
