from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer

from app.config import Config, selected_config

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = "/"
login_manager.login_message = None


def create_app(config: Config = selected_config):
    """Application factory method"""

    app = Flask(__name__)
    app.config.from_object(config)

    # Initialise extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    app.serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # Reset database
    from app.models import insertDummyData
    if app.config["RESET_DB"]:
        with app.app_context():
            db.drop_all()
            db.create_all()
            insertDummyData()

    # Register blueprints
    from app.views import auth, main
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app
