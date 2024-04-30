from datetime import date

import phonenumbers
from currency_converter import CurrencyConverter
from flask_login import current_user
from wtforms.validators import ValidationError

from app.models.enums import TherapyMode


class NotWhitespace:
    def __call__(self, form, field) -> None:
        if field.data and field.data.isspace():
            raise ValidationError(f"Invalid {field.name.replace('_', ' ').lower()}.")
        return


class ValidPassword:
    def __call__(self, form, field) -> None:
        if len(field.data) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        elif not any(char.isdigit() for char in field.data):
            raise ValidationError("Password must include at least one digit.")

        elif not any(char.isupper() for char in field.data):
            raise ValidationError(
                "Password must include at least one uppercase letter."
            )

        elif not any(char.islower() for char in field.data):
            raise ValidationError(
                "Password must include at least one lowercase letter."
            )

        return


class DateBeforeToday:
    def __call__(self, form, field) -> None:
        if field.data >= date.today():
            raise ValidationError("Date must be in the past.")
        return


class ValidPhoneNumber:
    def __call__(self, form, field) -> None:
        try:
            input_number = phonenumbers.parse(field.data, None)
        except phonenumbers.NumberParseException:
            raise ValidationError(
                "Please enter a valid phone number with the country code (e.g. +123456789)."
            )
        if not phonenumbers.is_valid_number(input_number):
            raise ValidationError("Invalid phone number.")
        return


class LocationRequired:
    def __call__(self, form, field) -> None:
        if (
            field.data == TherapyMode.IN_PERSON.name
            and current_user.therapist.location is None
        ):
            raise ValidationError("Location required for in-person appointments.")


class MinimumFeeAmount:
    def __call__(self, form, field) -> None:
        amount = form.fee_amount.data
        currency = form.fee_currency.data

        if not currency:
            return

        if currency != "USD":
            try:
                converter = CurrencyConverter()
                amount = converter.convert(
                    amount=amount, currency=currency, new_currency="USD"
                )
            except ValueError:
                return

        # Minimum amount for a Stripe charge
        if amount < 0.5:
            raise ValidationError(
                "Fee amount must be at least $0.50 USD or equivalent in charge currency"
            )
