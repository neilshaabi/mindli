from flask_sqlalchemy import SQLAlchemy

from app.models.issue import Issue
from app.models.language import Language
from app.models.session_format import SessionFormatModel
from app.models.user import User


def seed_db(db: SQLAlchemy) -> None:
    User.seed(db)
    Language.seed(db)
    Issue.seed(db)
    SessionFormatModel.seed(db)
    return
