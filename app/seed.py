from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app.models.appointment import Appointment
from app.models.appointment_notes import AppointmentNotes
from app.models.appointment_type import AppointmentType
from app.models.client import Client
from app.models.conversation import Conversation
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.message import Message
from app.models.therapist import Therapist
from app.models.title import Title
from app.models.user import User


# Seed required models in order
def seed_db(db: SQLAlchemy, use_fake_data: bool) -> None:
    Title.seed(db)
    Language.seed(db)
    Issue.seed(db)
    Intervention.seed(db)

    if use_fake_data:
        fake = Faker()
        User.seed(db, fake)
        Therapist.seed(db, fake)
        Client.seed(db, fake)
        Conversation.seed(db)
        Message.seed(db, fake)
        AppointmentType.seed(db, fake)
        Appointment.seed(db, fake)
        AppointmentNotes.seed(db, fake)
    return
