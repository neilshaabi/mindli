from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from app import mail
from app.models.appointment import Appointment
from app.models.enums import EmailSubject
from app.models.user import User


class EmailMessage:
    def __init__(
        self,
        recipient: User,
        subject: EmailSubject,
        mail: Mail = mail,
        context: dict = {},
        url_params: dict = {},
    ) -> None:
        self.mail = mail
        self.recipient = recipient
        self.subject = subject
        self.context = context
        self.url_params = url_params

        self.body = None
        self.link = None
        self.link_text = None
        self.send_with_token = False

        if self.subject == EmailSubject.EMAIL_VERIFICATION:
            self.body = f"Thanks for registering as a {recipient.role.value} with mindli! To continue setting up your account, please verify that this is your email address."
            self.link_text = "Verify Email"
            endpoint = "auth.email_verification"
            self.send_with_token = True

        elif self.subject == EmailSubject.PASSWORD_RESET:
            self.body = "Please use the link below to reset your account password."
            self.link_text = "Reset Password"
            endpoint = "auth.reset_password_self.send_with_token"
            self.send_with_token = True

        elif self.subject == EmailSubject.APPOINTMENT_SCHEDULED_CLIENT:
            self.body = "Your appointment has been successfully scheduled and is now awaiting confirmation by the therapist. You will be notified once confirmed."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_SCHEDULED_THERAPIST:
            self.body = "You have a new appointment scheduled and awaiting your confirmation. Please confirm the appointment at your earliest convenience."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.PAYMENT_FAILED_CLIENT:
            self.body = "Unfortunately, your recent payment attempt for an appointment was unsuccessful. Please view the appointment to reattempt the payment."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_CONFIRMED_CLIENT:
            appointment: Appointment = self.context["appointment"]
            self.body = f"Good news! Your appointment with {appointment.therapist.user.full_name} on {appointment.time.strftime('%A, %d %B %Y at %I:%M %p')} has been confirmed. Please review any preparation material in advance and reach out to your therapist if you have any questions before the appointment."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_RESCHEDULED:
            appointment: Appointment = self.context["appointment"]
            self.body = f"Your upcoming appointment with {appointment.other_user.full_name} has been rescheduled. Please note the new date and time are as follows: {appointment.time.strftime('%A, %d %B %Y at %I:%M %p')}."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_CANCELLED:
            appointment: Appointment = self.context["appointment"]
            self.body = f"We regret to inform you that your appointment scheduled for {appointment.time.strftime('%A, %d %B %Y at %I:%M %p')} has been cancelled. Please contact your therapist to schedule another appointment at your earliest convenience."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_NO_SHOW_CLIENT:
            appointment: Appointment = self.context["appointment"]
            self.body = f"We noticed that you were unable to attend your appointment with {appointment.other_user.full_name} scheduled for {appointment.time.strftime('%A, %d %B %Y at %I:%M %p')}. Please contact your therapist if this was an oversight or to schedule another appointment."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        else:
            print(f"Unhandled email subject {self.subject}")

        # Optionally add token to url
        if self.send_with_token:
            serialiser: URLSafeTimedSerializer = current_app.serialiser
            token = serialiser.dumps(recipient.email)
            self.url_params["token"] = token

        self.link = url_for(endpoint=endpoint, _external=True, **self.url_params)
        return

    def send(self) -> None:
        try:
            with current_app.app_context():
                # Send email to developer in dev environment
                recipients = (
                    [current_app.config["MAIL_USERNAME"]]
                    if current_app.config["ENV"] == "dev"
                    else [self.recipient.email]
                )

                # Construct and send message
                msg = Message(self.subject.value, recipients=recipients)
                msg.html = render_template("email.html", message=self)
                self.mail.send(msg)

        # Log errors
        except Exception as e:
            print(f"Failed to send email: {e}")

        return
