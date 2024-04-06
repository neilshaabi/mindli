from flask_sqlalchemy import SQLAlchemy


class SeedableMixin:
    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        pass


from .appointment_type import AppointmentType
from .associations import (
    client_issue,
    therapist_intervention,
    therapist_issue,
    therapist_language,
    therapist_title,
)
from .availability import Availability
from .client import Client
from .enums import Gender, ProfessionalTitle, TherapyMode, UserRole
from .intervention import Intervention
from .issue import Issue
from .language import Language
from .therapist import Therapist
from .title import Title
from .unavailability import Unavailability
from .user import User
