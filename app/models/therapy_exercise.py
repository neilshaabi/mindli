from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin
from app.models.appointment import Appointment


class TherapyExercise(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    appointment_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("appointment.id", ondelete="CASCADE"), index=True
    )
    title: so.Mapped[str] = so.mapped_column(sa.String(255))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    client_response: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    appointment: so.Mapped["Appointment"] = so.relationship(back_populates="exercise")

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        # Insert exercise for every appointment in database
        appointments = db.session.execute(db.select(Appointment)).scalars().all()
        for appointment in appointments:
            exercise = TherapyExercise(
                appointment_id=appointment.id,
                title=fake.sentence(nb_words=6),
                description=fake.text(max_nb_chars=200),
                client_response=fake.text(max_nb_chars=200),
                completed=fake.boolean(chance_of_getting_true=80),
            )
            db.session.add(exercise)
        db.session.commit()
        return
