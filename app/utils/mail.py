from typing import List

from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from app import mail
from app.config import DevConfig
from app.models.appointment import Appointment
from app.models.enums import EmailSubject
from app.models.user import User
from app.tasks import send_async_email


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
            self.body = f"Thanks for registering as a {recipient.role.value} with mindli! To continue setting up your account, please verify that this is your email address and follow the onboarding instructions in your profile."
            self.link_text = "Verify Email"
            endpoint = "auth.email_verification"
            self.send_with_token = True

        elif self.subject == EmailSubject.PASSWORD_RESET:
            self.body = "Please use the link below to reset your account password."
            self.link_text = "Reset Password"
            endpoint = "auth.reset_password_with_token"
            self.send_with_token = True

        elif self.subject == EmailSubject.APPOINTMENT_SCHEDULED_CLIENT:
            appointment: Appointment = self.context["appointment"]
            self.body = f"Your appointment with {appointment.therapist.user.full_name} on {appointment.time.strftime('%A, %-d %B %Y at %I:%M %p')} has been scheduled and is awaiting confirmation by the therapist. You will be notified once it has been confirmed."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_SCHEDULED_THERAPIST:
            appointment: Appointment = self.context["appointment"]
            self.body = f"You have a new appointment scheduled with {appointment.client.user.full_name} on {appointment.time.strftime('%A, %-d %B %Y at %I:%M %p')} and awaiting your confirmation. Please confirm the appointment at your earliest convenience."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.PAYMENT_FAILED_CLIENT:
            appointment: Appointment = self.context["appointment"]
            self.body = f"Unfortunately, your recent payment attempt for an appointment with {appointment.therapist.user.full_name} on {appointment.time.strftime('%A, %-d %B %Y at %I:%M %p')} was unsuccessful. Please view the appointment to reattempt the payment."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_CONFIRMED_CLIENT:
            appointment: Appointment = self.context["appointment"]
            self.body = f"Good news! Your appointment with {appointment.therapist.user.full_name} on {appointment.time.strftime('%A, %-d %B %Y at %I:%M %p')} has been confirmed. Please review any preparation material in advance and reach out to your therapist if you have any questions before the appointment."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_RESCHEDULED:
            appointment: Appointment = self.context["appointment"]
            self.body = f"Your upcoming appointment with {appointment.other_user.full_name} has been rescheduled. Please note the new date and time are as follows: {appointment.time.strftime('%A, %-d %B %Y at %I:%M %p')}."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_CANCELLED:
            appointment: Appointment = self.context["appointment"]
            self.body = f"We regret to inform you that your appointment scheduled for {appointment.time.strftime('%A, %-d %B %Y at %I:%M %p')} has been cancelled. Please contact your therapist to schedule another appointment at your earliest convenience."
            self.link_text = "View Appointment"
            endpoint = "appointments.appointment"
            self.send_with_token = False

        elif self.subject == EmailSubject.APPOINTMENT_NO_SHOW_CLIENT:
            appointment: Appointment = self.context["appointment"]
            self.body = f"We noticed that you were unable to attend your appointment with {appointment.other_user.full_name} scheduled for {appointment.time.strftime('%A, %-d %B %Y at %I:%M %p')}. Please contact your therapist if this was an oversight or to schedule another appointment."
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

    def prepare_email(self) -> str:
        html_body = render_template("email.html", message=self)
        return html_body

    def send(self, asynchronous: bool = True):
        with current_app.app_context():
            subject = self.subject.value
            recipients = (
                current_app.config["MAIL_USERNAME"]
                if isinstance(current_app.config, DevConfig)
                else [self.recipient.email]
            )
            html = render_template("email.html", message=self)

            try:
                # Send email synchronously
                if asynchronous and current_app.config["CELERY_ENABLED"]:
                    try:
                        send_async_email.delay(subject, recipients, html)
                        return
                    except Exception as e:
                        print(f"Failed to send email asynchronously: {e}")
                        pass

                # Try sending email synchronously if failed
                message = prepare_message(subject, recipients, html)
                self.mail.send(message)

            # Failed to send email
            except Exception as e:
                print(f"Failed to send email synchronously: {e}")
        return


def prepare_message(subject: str, recipients: List[str], html: str) -> Message:
    return Message(subject, recipients=recipients, html=html)


def send_appointment_update_email(
    appointment: Appointment, recipient: User, subject: EmailSubject
) -> None:
    email = EmailMessage(
        recipient=recipient,
        subject=subject,
        context={"appointment": appointment},
        url_params={"appointment_id": appointment.id},
    )
    email.send()
    return
