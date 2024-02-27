from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.user import User


class Therapist(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    country: so.Mapped[str] = so.mapped_column(sa.String(50))
    affilitation: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    bio: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    link: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    location: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    registrations: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    qualifications: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    years_of_experience: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)

    user: so.Mapped["User"] = so.relationship(back_populates="therapist")
    languages: so.Mapped[List["Language"]] = so.relationship(
        secondary="therapist_language", back_populates="therapists"
    )
    specialisations: so.Mapped[List["Issue"]] = so.relationship(
        secondary="therapist_issue", back_populates="therapists"
    )
    session_types: so.Mapped[List["SessionType"]] = so.relationship(
        back_populates="therapist"
    )
    availabilities: so.Mapped[List["Availability"]] = so.relationship(
        back_populates="therapist"
    )
    unavailabilities: so.Mapped[List["Unavailability"]] = so.relationship(
        back_populates="therapist"
    )
