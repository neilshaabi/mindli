from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.enums import TherapyMode


class AppointmentType(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id", ondelete="CASCADE"), index=True
    )
    name: so.Mapped[str] = so.mapped_column(
        sa.String(255)
    )  # e.g. "Initial Consultation"
    session_duration: so.Mapped[int] = so.mapped_column(sa.Integer)  # In minutes
    fee_amount: so.Mapped[float] = so.mapped_column(sa.Float)
    fee_currency: so.Mapped[str] = so.mapped_column(sa.String(3))
    therapy_mode: so.Mapped[Optional["TherapyMode"]] = so.mapped_column(
        sa.Enum(TherapyMode)
    )
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="appointment_types")
