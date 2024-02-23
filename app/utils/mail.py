from enum import Enum, unique
from typing import Optional

from flask import render_template, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from app.models import User


@unique
class EmailSubject(Enum):
    EMAIL_VERIFICATION = "Email verification"
    PASSWORD_RESET = "Password reset"


class EmailMessage:
    
    def __init__(
        self,
        mail: Mail,
        subject: EmailSubject,
        recipient: User,
        serialiser: Optional[URLSafeTimedSerializer],
    ) -> None:
        
        self.mail = mail
        self.recipient = recipient
        self.subject = subject.value
        self.body = None
        self.link = None
        self.link_text = None

        if self.subject == EmailSubject.EMAIL_VERIFICATION.value:
            self.body = "Thanks for joining mindli! To continue setting up your account, please verify that this is your email address."
            self.link_text = "Verify Email"
            endpoint = "auth.email_verification"

        elif self.subject == EmailSubject.PASSWORD_RESET.value:
            self.body = "Please use the link below to reset your account password."
            self.link_text = "Reset Password"
            endpoint = "auth.reset_password"

        token = serialiser.dumps(recipient.email) if serialiser else None
        self.link = url_for(endpoint=endpoint, token=token, _external=True)
        return

    def send(self) -> None:
        msg = Message(self.subject, recipients=[self.recipient.email])
        # msg = Message(self.subject, recipients=["neilshaabi@gmail.com"])
        msg.html = render_template("email.html", message=self)
        self.mail.send(msg)
        return
