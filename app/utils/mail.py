from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from app import mail
from app.models.enums import EmailSubject
from app.models.user import User


class EmailMessage:
    def __init__(
        self,
        recipient: User,
        subject: EmailSubject,
        mail: Mail = mail,
        **url_parameters: dict,
    ) -> None:
        self.mail = mail
        self.recipient = recipient
        self.subject = subject
        self.url_params = url_parameters
        self.body = None
        self.link = None
        self.link_text = None
        with_token = False

        if self.subject == EmailSubject.EMAIL_VERIFICATION:
            self.body = f"Thanks for registering as a {recipient.role.value} with mindli! To continue setting up your account, please verify that this is your email address."
            self.link_text = "Verify Email"
            endpoint = "auth.email_verification"
            with_token = True

        elif self.subject == EmailSubject.PASSWORD_RESET:
            self.body = "Please use the link below to reset your account password."
            self.link_text = "Reset Password"
            endpoint = "auth.reset_password_get"
            with_token = True

        elif self.subject == EmailSubject.APPOINTMENT_SCHEDULED_CLIENT:
            self.body = "Your appointment has been successfully scheduled and is now awaiting confirmation by the therapist. You will be notified once confirmed."
            self.link_text = "View Appointment"
            endpoint = "appointments.view_appointment"
            with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_SCHEDULED_THERAPIST:
            self.body = "You have a new appointment scheduled and awaiting your confirmation. Please confirm the appointment at your earliest convenience."
            self.link_text = "View Appointment"
            endpoint = "appointments.view_appointment"
            with_token = False

        elif self.subject == EmailSubject.PAYMENT_FAILED_CLIENT:
            self.body = "Unfortunately, your recent payment attempt for an appointment was unsuccessful. Please view the appointment to reattempt the payment."
            self.link_text = "View Appointment"
            endpoint = "appointments.view_appointment"
            with_token = False

        else:
            print(f"Unhandled email subject {self.subject}")

        # Optionally add token to url
        if with_token:
            serialiser: URLSafeTimedSerializer = current_app.serialiser
            token = serialiser.dumps(recipient.email)
            self.url_params["token"] = token

        self.link = url_for(endpoint=endpoint, _external=True, **self.url_params)
        return

    def send(self) -> None:
        msg = Message(self.subject.value, recipients=[self.recipient.email])
        msg.html = render_template("email.html", message=self)
        self.mail.send(msg)
        return
