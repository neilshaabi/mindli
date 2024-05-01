import os
from http.client import HTTPException

import stripe
from flask import Flask, Response, render_template
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer

from app.config import CONFIGS, Config

# Declare extensions for global use
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()

# Configure login manager
login_manager.login_view = "/login"
login_manager.login_message = None

from app.models.user import User  # noqa: E402


# Define user loader to associate current user with User instance
@login_manager.user_loader
def load_user(user_id: str) -> User:
    return db.session.execute(
        db.select(User).filter_by(id=int(user_id))
    ).scalar_one_or_none()


# Flask application factory
def create_app(config: Config = None, celery_worker: bool = False):
    if not config:
        config = CONFIGS[os.environ["ENV"]]

    app = Flask(__name__)
    app.config.from_object(config)

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    app.serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # Configure Stripe
    stripe.api_key = app.config["STRIPE_SECRET_KEY"]
    stripe.api_version = "2023-10-16"

    # Initialise CSRF protection conditionally
    if app.config["WTF_CSRF_ENABLED"]:
        csrf.init_app(app)

    # Initialise Celery
    from app.utils.celery import celery_init_app

    app.celery = celery_init_app(app)
    if celery_worker:
        return app

    # Register context processor to inject global variables
    @app.context_processor
    def inject_globals():
        from app.models.enums import UserRole

        return {
            "UserRole": UserRole,
            "STRIPE_PUBLISHABLE_KEY": app.config["STRIPE_PUBLISHABLE_KEY"],
        }

    with app.app_context():
        from app.models import seed_db

        # Reset database
        if app.config["RESET_DB"]:
            db.drop_all()
            db.create_all()
            db.session.commit()

            # Seed database
            seed_db(db=db, use_fake_data=app.config["FAKE_DATA"])

    # Register handler to redirect to custom error page
    if app.config["ERROR_HANDLER"]:

        @app.errorhandler(Exception)
        def handle_exception(e: Exception) -> Response:
            print(f"Error: {e}")
            return render_template(
                "error.html",
                error=e,
                is_http_exception=isinstance(e, HTTPException),
            )

    # Register blueprints with endpoints
    from app.views import (appointment_types, appointments, auth, clients,
                           main, messages, profile)
    from app.views import stripe as stripe_bp
    from app.views import therapists, treatment_plans, users

    app.register_blueprint(appointment_types.bp)
    app.register_blueprint(appointments.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(clients.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(stripe_bp.bp)
    app.register_blueprint(therapists.bp)
    app.register_blueprint(treatment_plans.bp)
    app.register_blueprint(users.bp)

    return app
