from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.enums import SessionFormat


class SessionType(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id"), index=True
    )
    name: so.Mapped[str] = so.mapped_column(
        sa.String(255)
    )  # e.g. "Initial Consultation"
    session_duration: so.Mapped[int] = so.mapped_column(sa.Integer)  # In minutes
    fee_amount: so.Mapped[float] = so.mapped_column(sa.Float)
    fee_currency: so.Mapped[str] = so.mapped_column(sa.String(3))
    session_format: so.Mapped[Optional["SessionFormat"]] = so.mapped_column(
        sa.Enum(SessionFormat)
    )
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="session_types")
