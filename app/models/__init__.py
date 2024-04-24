from typing import Optional

from faker import Faker
from flask_sqlalchemy import SQLAlchemy


class SeedableMixin:
    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Optional[Faker] = None) -> None:
        pass


from .appointment import Appointment
from .appointment_notes import AppointmentNotes
from .appointment_type import AppointmentType
from .associations import (
    client_issue,
    note_intervention,
    note_issue,
    therapist_intervention,
    therapist_issue,
    therapist_language,
    therapist_title,
)
from .client import Client
from .conversation import Conversation
from .enums import Gender, TherapyMode, UserRole
from .intervention import Intervention
from .issue import Issue
from .language import Language
from .message import Message
from .therapist import Therapist
from .title import Title
from .user import User
