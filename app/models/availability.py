from datetime import time

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class Availability(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id", ondelete="CASCADE"), index=True
    )
    day_of_week: so.Mapped[int] = so.mapped_column(sa.Integer)  # 0=Monday, 6=Sunday
    start_time: so.Mapped[time] = so.mapped_column(sa.Time)
    end_time: so.Mapped[time] = so.mapped_column(sa.Time)

    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="availabilities")
