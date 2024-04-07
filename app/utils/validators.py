import phonenumbers
from wtforms.validators import ValidationError


class WhitespaceValidator:
    def __call__(self, form, field):
        if field.data and field.data.isspace():
            raise ValidationError(f"Invalid {field.name.replace('_', ' ').lower()}.")
        return


class PasswordValidator:
    def __call__(self, form, field):
        error = None

        if len(field.data) < 8:
            error = "Password must be at least 8 characters long."

        elif not any(char.isdigit() for char in field.data):
            error = "Password must include at least one digit."

        elif not any(char.isupper() for char in field.data):
            error = "Password must include at least one uppercase letter."

        elif not any(char.islower() for char in field.data):
            error = "Password must include at least one lowercase letter."

        if error:
            raise ValidationError(error)

        return


class PhoneNumberValidator:
    def __call__(self, form, field):
        try:
            input_number = phonenumbers.parse(field.data, None)
        except phonenumbers.NumberParseException:
            raise ValidationError(
                "Please enter a valid phone number with the country code (e.g. +123456789)."
            )
        if not phonenumbers.is_valid_number(input_number):
            raise ValidationError("Invalid phone number.")
        return
