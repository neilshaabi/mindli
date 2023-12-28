import os

basedir: str = os.path.abspath(os.path.dirname(__file__))


# Default config values
class Config(object):
    SECRET_KEY: str = os.environ['SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Flask Mail setup
    MAIL_SERVER: str = 'smtppro.zoho.eu'
    MAIL_PORT: int = 465
    MAIL_USE_SSL: bool = True
    MAIL_USE_TLS: bool = False
    MAIL_USERNAME: str = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD: str = os.environ['MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER: str = MAIL_USERNAME
    MAIL_SUPPRESS_SEND: bool = False


# Config values for running app in development
class DevConfig(Config):
    DEBUG: bool = True
    RESET_DB: bool = True
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{os.path.join(basedir, 'mindli.sqlite')}"


# Config values for running app in production
class ProdConfig(Config):
    DEBUG: bool = False
    RESET_DB: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.environ['DATABASE_URL']
