import os

from dotenv import load_dotenv

basedir: str = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


# Default config values
class Config(object):
    ENV: str = os.environ["ENV"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]  # os.urandom(12).hex()
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Flask Mail setup
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 465
    MAIL_USE_SSL: bool = True
    MAIL_USE_TLS: bool = False
    MAIL_USERNAME: str = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD: str = os.environ["MAIL_PASSWORD"]
    MAIL_DEFAULT_SENDER: str = MAIL_USERNAME
    MAIL_SUPPRESS_SEND: bool = False


class DevConfig(Config):
    DEBUG: bool = True
    RESET_DB: bool = True
    FAKE_DATA: bool = True
    WTF_CSRF_ENABLED: str = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///" + os.path.join(basedir, "mindli.sqlite")


class ProdConfig(Config):
    DEBUG: bool = False
    RESET_DB: bool = False
    FAKE_DATA: bool = False
    WTF_CSRF_ENABLED: str = True
    SQLALCHEMY_DATABASE_URI: str = os.environ["DATABASE_URL"]


class TestConfig(Config):
    DEBUG: bool = False
    RESET_DB: bool = True
    FAKE_DATA: bool = True
    WTF_CSRF_ENABLED: str = False
    SQLALCHEMY_DATABASE_URI: str = "sqlite://"  # Use in-memory database


CONFIGS: "dict[str, Config]" = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "test": TestConfig,
}
