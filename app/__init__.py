import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer

from app.config import CONFIGS, Config

db = SQLAlchemy()
migrate = Migrate()
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
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    app.serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # Register blueprints
    from app.views import auth, main

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app
