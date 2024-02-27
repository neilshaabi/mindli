from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, RadioField, StringField
from wtforms.validators import DataRequired, Email, Length

from app.utils.validators import PasswordValidator


class LoginForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
    )


class RegisterForm(FlaskForm):
    role = RadioField(
        "Role",
        choices=[("therapist", "Therapist"), ("client", "Client")],
        validators=[DataRequired()],
    )
    first_name = StringField(
        "First name", validators=[DataRequired(), Length(min=2, max=50)]
    )
    last_name = StringField(
        "Last name", validators=[DataRequired(), Length(min=2, max=50)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), PasswordValidator()]
    )


class EmailForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Email()])


class ResetPasswordForm(FlaskForm):
    email = HiddenField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField(
        "New password", validators=[DataRequired(), PasswordValidator()]
    )
    password_confirmation = PasswordField(
        "Password confirmation", validators=[DataRequired()]
    )
