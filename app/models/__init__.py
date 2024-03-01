from flask_sqlalchemy import SQLAlchemy


class SeedableMixin:
    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        pass


from .associations import (
    client_format,
    client_issue,
    therapist_format,
    therapist_issue,
    therapist_language,
)
from .availability import Availability
from .client import Client
from .enums import Gender, SessionFormat, UserRole
from .issue import Issue
from .language import Language
from .session_format import SessionFormatModel
from .session_type import SessionType
from .therapist import Therapist
from .unavailability import Unavailability
from .user import User
