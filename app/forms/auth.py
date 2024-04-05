from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, RadioField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length

from app.models.enums import UserRole
from app.utils.validators import PasswordValidator


class LoginForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
    )
    submit = SubmitField("Continue")


class RegisterForm(FlaskForm):
    role = RadioField(
        "Role",
        choices=[
            (UserRole.THERAPIST.value, UserRole.THERAPIST.value.capitalize()),
            (UserRole.CLIENT.value, UserRole.CLIENT.value.capitalize()),
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


class VerifyEmailForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    submit = SubmitField("Resend Email")


class InitiatePasswordResetForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    submit = SubmitField("Continue")


class ResetPasswordForm(FlaskForm):
    email = HiddenField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField(
        "New password", validators=[DataRequired(), PasswordValidator()]
    )
    password_confirmation = PasswordField(
        "Password confirmation", validators=[DataRequired()]
    )
    submit = SubmitField("Reset Password")
