from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email

from app.utils.validators import PasswordValidator, UserCredentialsValidator


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), PasswordValidator(), UserCredentialsValidator()],
    )
