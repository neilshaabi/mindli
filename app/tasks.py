from typing import List

from celery import shared_task
from flask import current_app

from app import mail


@shared_task
def send_async_email(subject: str, recipients: List[str], html: str) -> None:
    with current_app.app_context():
        from app.utils.mail import prepare_message

        message = prepare_message(subject, recipients, html)
        mail.send(message)
    return
