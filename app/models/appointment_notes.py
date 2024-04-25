import random
from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin
from app.models.appointment import Appointment
from app.models.intervention import Intervention
from app.models.issue import Issue


class AppointmentNotes(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    appointment_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("appointment.id", ondelete="CASCADE"), index=True
    )
    text: so.Mapped[str] = so.mapped_column(sa.Text)
    efficacy: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    last_updated: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.now()
    )

    issues: so.Mapped[List["Issue"]] = so.relationship(
        secondary="note_issue", back_populates="notes"
    )
    interventions: so.Mapped[List["Intervention"]] = so.relationship(
        secondary="note_intervention", back_populates="notes"
    )

    appointment: so.Mapped["Appointment"] = so.relationship(back_populates="notes")

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        # Insert note for every appointment in database
        appointments = db.session.execute(db.select(Appointment)).scalars().all()
        for appointment in appointments:
            note = AppointmentNotes(
                appointment_id=appointment.id,
                text=fake.sentence(nb_words=random.randint(20, 50)),
                efficacy=random.randint(1, 5),
            )
            db.session.add(note)
            note.issues = appointment.client.issues
            note.interventions = appointment.therapist.interventions
        db.session.commit()
        return
