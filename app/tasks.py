from flask_mail import Message
from flask import current_app
from celery import shared_task
from app import mail

@shared_task
def send_async_email(message: Message):
    with current_app.app_context():
        mail.send(message)
    return