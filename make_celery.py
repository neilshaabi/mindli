
from app import create_app

# Required to use celery commands
flask_app = create_app()
celery = flask_app.celery