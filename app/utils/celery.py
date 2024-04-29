from app import create_app
from flask import Flask
from celery import Celery, Task

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    celery.Task = FlaskTask
    return celery

# Required to use celery commands
flask_app = create_app()
celery = flask_app.celery