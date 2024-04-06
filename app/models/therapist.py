from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin
from app.models.enums import UserRole
from app.models.user import User


class Therapist(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    country: so.Mapped[str] = so.mapped_column(sa.String(50))
    link: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    location: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    years_of_experience: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    qualifications: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    registrations: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    user: so.Mapped["User"] = so.relationship(back_populates="therapist")
    languages: so.Mapped[List["Language"]] = so.relationship(
        secondary="therapist_language", back_populates="therapists"
    )
    specialisations: so.Mapped[List["Issue"]] = so.relationship(
        secondary="therapist_issue", back_populates="therapists"
    )
    session_formats: so.Mapped[List["SessionFormatModel"]] = so.relationship(
        secondary="therapist_format", back_populates="therapists"
    )
    session_types: so.Mapped[List["SessionType"]] = so.relationship(
        back_populates="therapist", cascade="all, delete-orphan"
    )
    availabilities: so.Mapped[List["Availability"]] = so.relationship(
        back_populates="therapist", cascade="all, delete-orphan"
    )
    unavailabilities: so.Mapped[List["Unavailability"]] = so.relationship(
        back_populates="therapist", cascade="all, delete-orphan"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        fake_user_therapist = db.session.execute(
            db.select(User).filter_by(role=UserRole.THERAPIST)
        ).scalar_one_or_none()

        fake_therapist = Therapist(
            user_id=fake_user_therapist.id,
            country="Singapore",
            link="http://example.com",
            location="21 Lower Kent Ridge Rd, Singapore 119077",
            years_of_experience=5,
            qualifications="Doctor of Psychology (Psy.D.) in Clinical Psychology, National University of Singapore (NUS)",
            registrations="Singapore Psychological Society (SPS)",
        )
        db.session.add(fake_therapist)
        db.session.commit()
        return
