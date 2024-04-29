from celery import Celery, Task
from flask import Flask

from app import create_app


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.import_name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    return celery_app


# Required to use celery commands
flask_app = create_app()
celery = flask_app.celery
