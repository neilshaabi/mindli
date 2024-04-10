import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer

from app.config import CONFIGS, Config, ProdConfig

# Declare extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()

login_manager.login_view = "/login"
login_manager.login_message = None

from app.models.user import User  # noqa: E402


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.execute(db.select(User).filter_by(id=int(user_id))).scalar_one()


def create_app(config: Config = CONFIGS[os.environ["ENV"]]):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    app.serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # Initialise CSRF protection for forms
    if app.config["WTF_CSRF_ENABLED"]:
        csrf.init_app(app)

    # Register context processor to inject global variables
    @app.context_processor
    def inject_globals():
        from app.models.enums import UserRole

        return {
            "UserRole": UserRole,
        }

    # Reset and seed database
    from app.seed import seed_db

    if app.config["RESET_DB"]:
        with app.app_context():
            db.drop_all()
            db.create_all()
            db.session.commit()
            seed_db(db)

    # Register blueprints with endpoints
    from app.views import appointments, auth, main, profile, therapists

    app.register_blueprint(appointments.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(therapists.bp)

    # Register handler to redirect to custom error page
    from app.views.errors import register_error_handlers

    if config == ProdConfig:
        register_error_handlers(app)

    return app
