from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin
from app.models.appointment_type import AppointmentType
from app.models.client import Client
from app.models.enums import AppointmentStatus
from app.models.therapist import Therapist


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
    status: so.Mapped["AppointmentStatus"] = so.mapped_column(
        sa.Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED
    )

    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="appointments")
    client: so.Mapped["Client"] = so.relationship(back_populates="appointments")
    appointment_type: so.Mapped["AppointmentType"] = so.relationship(
        back_populates="appointments"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        pass
