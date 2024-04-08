from wtforms import (HiddenField, PasswordField, RadioField, StringField,
                     SubmitField)
from wtforms.validators import DataRequired, Email, Length

from app.forms import CustomFlaskForm
from app.models.enums import UserRole
from app.utils.validators import PasswordValidator


class LoginForm(CustomFlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
    )
    submit = SubmitField("Continue")


class RegisterForm(CustomFlaskForm):
    role = RadioField(
        "Role",
        choices=[
            (UserRole.THERAPIST.value, UserRole.THERAPIST.value),
            (UserRole.CLIENT.value, UserRole.CLIENT.value),
        ],
        validators=[DataRequired()],
    )
    first_name = StringField(
        "First name", validators=[DataRequired(), Length(min=1, max=50)]
    )
    last_name = StringField(
        "Last name", validators=[DataRequired(), Length(min=1, max=50)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), PasswordValidator()]
    )
    submit = SubmitField("Register")


class VerifyEmailForm(CustomFlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    submit = SubmitField("Resend Email")


class InitiatePasswordResetForm(CustomFlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    submit = SubmitField("Continue")


class ResetPasswordForm(CustomFlaskForm):
    email = HiddenField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField(
        "New password", validators=[DataRequired(), PasswordValidator()]
    )
    password_confirmation = PasswordField(
        "Password confirmation", validators=[DataRequired()]
    )
    submit = SubmitField("Reset Password")
