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
from .associations import (client_issue, note_intervention, note_issue,
                           therapist_intervention, therapist_issue,
                           therapist_language, therapist_title)
from .client import Client
from .conversation import Conversation
from .enums import Gender, TherapyMode, UserRole
from .intervention import Intervention
from .issue import Issue
from .language import Language
from .message import Message
from .therapist import Therapist
from .therapy_exercise import TherapyExercise
from .title import Title
from .treatment_plan import TreatmentPlan
from .user import User


# Seed database models in order
def seed_db(db: SQLAlchemy, use_fake_data: bool) -> None:
    
    # Insert static data
    Title.seed(db)
    Language.seed(db)
    Issue.seed(db)
    Intervention.seed(db)

    # Insert dummy data conditionally
    if use_fake_data:
        fake = Faker()
        User.seed(db, fake)
        Therapist.seed(db, fake)
        Client.seed(db, fake)
        TreatmentPlan.seed(db)
        Conversation.seed(db)
        Message.seed(db, fake)
        AppointmentType.seed(db, fake)
        Appointment.seed(db, fake)
        AppointmentNotes.seed(db, fake)
        TherapyExercise.seed(db, fake)
    return
