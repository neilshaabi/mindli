import random
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.constants import EXAMPLE_CLIENT_EMAIL, EXAMPLE_THERAPIST_EMAIL
from app.models import SeedableMixin
from app.models.client import Client
from app.models.enums import AppointmentStatus, PaymentStatus, UserRole
from app.models.user import User


class Appointment(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id"), index=True
    )
    client_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("client.id"), index=True)
    appointment_type_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("appointment_type.id", ondelete="CASCADE"), index=True
    )
    time: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    appointment_status: so.Mapped["AppointmentStatus"] = so.mapped_column(
        sa.Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED
    )
    payment_status: so.Mapped["PaymentStatus"] = so.mapped_column(
        sa.Enum(PaymentStatus), default=PaymentStatus.PENDING
    )

    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="appointments")
    client: so.Mapped["Client"] = so.relationship(back_populates="appointments")
    appointment_type: so.Mapped["AppointmentType"] = so.relationship(
        back_populates="appointments"
    )
    notes: so.Mapped["AppointmentNotes"] = so.relationship(
        back_populates="appointment",
    )
    exercise: so.Mapped["TherapyExercise"] = so.relationship(
        back_populates="appointment",
    )

    @property
    def this_user(self) -> User:
        if current_user.role == UserRole.THERAPIST:
            return self.therapist.user
        elif current_user.role == UserRole.CLIENT:
            return self.client.user

    @property
    def other_user(self) -> User:
        if current_user.role == UserRole.THERAPIST:
            return self.client.user
        elif current_user.role == UserRole.CLIENT:
            return self.therapist.user

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        # Helper function to adjust minutes to :00, :15, :30, or :45
        def generate_reasonable_datetime() -> datetime:
            dt = fake.future_datetime(end_date="+30d", tzinfo=None)
            minutes = random.choice([0, 15, 30, 45])
            dt = dt.replace(minute=minutes, second=0, microsecond=0)
            return dt

        appointments = []

        # Fetch example therapist and client
        example_therapist_user = db.session.execute(
            db.select(User).filter_by(email=EXAMPLE_THERAPIST_EMAIL)
        ).scalar_one()

        example_client_user = db.session.execute(
            db.select(User).filter_by(email=EXAMPLE_CLIENT_EMAIL)
        ).scalar_one()

        # Retrieve all clients excluding the example client
        other_clients = (
            db.session.execute(
                db.select(Client).where(Client.id != example_client_user.client.id)
            )
            .scalars()
            .all()
        )

        # Select five different clients including example to make appointments with
        selected_clients = [example_client_user.client]
        selected_clients.extend(other_clients[:4])

        # Insert between 2-5 appointments between the example therapist and selected clients
        for client in selected_clients:
            for _ in range(random.randint(2, 4)):
                appointment = Appointment(
                    therapist_id=example_therapist_user.therapist.id,
                    client_id=client.id,
                    appointment_type_id=random.choice(
                        example_therapist_user.therapist.active_appointment_types
                    ).id,
                    time=generate_reasonable_datetime(),
                    appointment_status=random.choice(list(AppointmentStatus)),
                    payment_status=random.choice(list(PaymentStatus)),
                )
                appointments.append(appointment)

        db.session.add_all(appointments)
        db.session.commit()
        return
