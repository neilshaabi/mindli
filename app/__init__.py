import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer

from app.config import CONFIGS, Config

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = "/"
login_manager.login_message = None

selected_config = CONFIGS[os.environ["ENV"]]

def create_app(config: Config = selected_config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialise extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    app.serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # Reset database when not in production
    if app.config["RESET_DB"]:
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            # Insert fake data
            if app.config["FAKE_DATA"]:
                from app.models import insertDummyData
                insertDummyData()

    # Register blueprints
    from app.views import auth, main
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app
