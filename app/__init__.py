from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer
from flask_sqlalchemy import SQLAlchemy

from app.config import config

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = "/"
login_manager.login_message = None

def create_app():
    """Application factory method"""
    
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialise extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    app.serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    
    # Reset database
    from app.db import resetDatabase
    if app.config["RESET_DB"]:
        with app.app_context():
            resetDatabase()

    # Register blueprints
    from app.views import auth, main
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    
    return app
