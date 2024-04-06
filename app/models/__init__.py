from flask_sqlalchemy import SQLAlchemy


class SeedableMixin:
    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        pass


from .associations import (
    client_issue,
    therapist_issue,
    therapist_language,
)
from .availability import Availability
from .client import Client
from .enums import Gender, TherapyMode, UserRole
from .issue import Issue
from .language import Language
from .appointment_type import AppointmentType
from .therapist import Therapist
from .unavailability import Unavailability
from .user import User
