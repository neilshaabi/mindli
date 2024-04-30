import os

from dotenv import load_dotenv

basedir: str = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


# Default configuration values
class Config(object):
    ENV: str = os.environ["ENV"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]  # os.urandom(12).hex()
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Flask Mail configuration
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 465
    MAIL_USE_SSL: bool = True
    MAIL_USE_TLS: bool = False
    MAIL_USERNAME: str = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD: str = os.environ["MAIL_PASSWORD"]
    MAIL_DEFAULT_SENDER: str = MAIL_USERNAME
    MAIL_SUPPRESS_SEND: bool = False

    # Stripe configuration
    STRIPE_SECRET_KEY: str = os.environ["STRIPE_SECRET_KEY"]
    STRIPE_PUBLISHABLE_KEY: str = os.environ["STRIPE_PUBLISHABLE_KEY"]
    STRIPE_WEBHOOK_SECRET: str = os.environ["STRIPE_WEBHOOK_SECRET"]


class DevConfig(Config):
    DEBUG: bool = True
    RESET_DB: bool = True
    FAKE_DATA: bool = True
    WTF_CSRF_ENABLED: str = True
    ERROR_HANDLER: bool = False
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///" + os.path.join(basedir, "mindli.sqlite")
    CELERY_ENABLED: bool = True
    CELERY: dict = {
        "broker_url": "redis://localhost",
        "result_backend": "redis://localhost",
        "task_ignore_result": True,
    }


class ProdConfig(Config):
    DEBUG: bool = False
    RESET_DB: bool = False
    FAKE_DATA: bool = False
    WTF_CSRF_ENABLED: str = True
    ERROR_HANDLER: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ["DATABASE_URL"]


class TestConfig(Config):
    DEBUG: bool = False
    RESET_DB: bool = True
    FAKE_DATA: bool = True
    WTF_CSRF_ENABLED: str = False
    ERROR_HANDLER: bool = False
    SQLALCHEMY_DATABASE_URI: str = "sqlite://"  # Use in-memory database

    CELERY_ENABLED: bool = False
    CELERY: dict = {
        "broker_url": "memory://",
        "result_backend": "db+sqlite:///test.sqlite",
        "task_ignore_result": True,
        "task_always_eager": True,
        "task_eager_propagates": True,
    }


CONFIGS: "dict[str, Config]" = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "test": TestConfig,
}
