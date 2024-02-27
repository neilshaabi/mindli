from flask_wtf import FlaskForm
from wtforms import PasswordField, RadioField, StringField
from wtforms.validators import DataRequired, Email, Length

from app.utils.validators import PasswordValidator


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
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
        "First Name", validators=[DataRequired(), Length(min=2, max=50)]
    )
    last_name = StringField(
        "Last Name", validators=[DataRequired(), Length(min=2, max=50)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), PasswordValidator()]
    )
