from enum import Enum, unique

from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from app import mail
from app.models import User


@unique
class EmailSubject(Enum):
    EMAIL_VERIFICATION = "Email verification"
    PASSWORD_RESET = "Password reset"


class EmailMessage:
    def __init__(
        self,
        recipient: User,
        subject: EmailSubject,
        mail: Mail = mail,
    ) -> None:
        self.mail = mail
        self.recipient = recipient
        self.subject = subject.value
        self.body = None
        self.link = None
        self.link_text = None

        with_token = False

        if self.subject == EmailSubject.EMAIL_VERIFICATION.value:
            self.body = f"Thanks for registering as a {recipient.role.value} with mindli! To continue setting up your account, please verify that this is your email address."
            self.link_text = "Verify Email"
            endpoint = "auth.email_verification"
            with_token = True

        elif self.subject == EmailSubject.PASSWORD_RESET.value:
            self.body = "Please use the link below to reset your account password."
            self.link_text = "Reset Password"
            endpoint = "auth.reset_password_get"
            with_token = True

        # Optionally add token to url
        if with_token:
            serialiser: URLSafeTimedSerializer = current_app.serialiser
            token = serialiser.dumps(recipient.email)
        else:
            token = None

        self.link = url_for(endpoint=endpoint, token=token, _external=True)

        return

    def send(self) -> None:
        msg = Message(self.subject, recipients=[self.recipient.email])
        msg.html = render_template("email.html", message=self)
        self.mail.send(msg)
        return
