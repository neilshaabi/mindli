from datetime import date
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class Unavailability(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id"), index=True
    )
    start_date: so.Mapped[date] = so.mapped_column(sa.Date)
    end_date: so.Mapped[date] = so.mapped_column(sa.Date)
    reason: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    therapist: so.Mapped["Therapist"] = so.relationship(
        back_populates="unavailabilities"
    )
