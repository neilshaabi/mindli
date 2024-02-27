import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer

from app.config import CONFIGS, Config, ProdConfig

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()

login_manager.login_view = "/"
login_manager.login_message = None

from app.models import User  # noqa: E402


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.execute(db.select(User).filter_by(id=int(user_id))).scalar_one()


selected_config = CONFIGS[os.environ["ENV"]]


def create_app(config: Config = selected_config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app) if not app.config["TESTING"] else None
    mail.init_app(app)
    login_manager.init_app(app)
    app.serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # Register blueprints
    from app.views import auth, errors, main

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    if config == ProdConfig:
        errors.register_error_handlers(app)

    return app
