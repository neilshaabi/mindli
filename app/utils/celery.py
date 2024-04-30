from typing import List

from celery import Celery, Task, shared_task
from flask import Flask, current_app

from app import mail


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.import_name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    return celery_app


@shared_task
def send_async_email(subject: str, recipients: List[str], html: str) -> None:
    with current_app.app_context():
        from app.utils.mail import prepare_message

        message = prepare_message(subject, recipients, html)
        mail.send(message)
    return
