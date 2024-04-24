from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db

# Assuming Intervention and Issue are defined somewhere else in your models
from app.models.intervention import Intervention
from app.models.issue import Issue


class AppointmentNotes(db.Model):
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
