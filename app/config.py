import os

from dotenv import load_dotenv

basedir: str = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


# Default config values
class Config(object):
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
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///" + os.path.join(basedir, "mindli.sqlite")


class ProdConfig(Config):
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.environ["DATABASE_URL"]


class TestConfig(Config):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite://"  # Use in-memory database


CONFIGS: "dict[str, Config]" = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "test": TestConfig,
}
