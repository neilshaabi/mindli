from datetime import date, time
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class Availability(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id"), index=True
    )
    day_of_week: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer
    )  # 0=Monday, 6=Sunday, None for specific dates
    start_time: so.Mapped[Optional[time]] = so.mapped_column(sa.Time)
    end_time: so.Mapped[Optional[time]] = so.mapped_column(sa.Time)
    specific_date: so.Mapped[Optional[date]] = so.mapped_column(
        sa.Date
    )  # For non-recurring availability

    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="availabilities")
