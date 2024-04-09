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
    years_of_experience: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    qualifications: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    registrations: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    country: so.Mapped[str] = so.mapped_column(sa.String(50))
    location: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    link: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))

    user: so.Mapped["User"] = so.relationship(back_populates="therapist")
    titles: so.Mapped[List["Title"]] = so.relationship(
        secondary="therapist_title", back_populates="therapists"
    )
    languages: so.Mapped[List["Language"]] = so.relationship(
        secondary="therapist_language", back_populates="therapists"
    )
    specialisations: so.Mapped[List["Issue"]] = so.relationship(
        secondary="therapist_issue", back_populates="therapists"
    )
    interventions: so.Mapped[List["Intervention"]] = so.relationship(
        secondary="therapist_intervention", back_populates="therapists"
    )
    appointment_types: so.Mapped[List["AppointmentType"]] = so.relationship(
        back_populates="therapist", cascade="all, delete-orphan"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        fake_user_therapist = db.session.execute(
            db.select(User).filter_by(role=UserRole.THERAPIST)
        ).scalar_one_or_none()

        fake_therapist = Therapist(
            user_id=fake_user_therapist.id,
            years_of_experience=5,
            country="Singapore",
            location="21 Lower Kent Ridge Rd, Singapore 119077",
            qualifications="Doctor of Psychology in Clinical Psychology, NUS",
            registrations="Singapore Psychological Society (SPS)",
        )
        db.session.add(fake_therapist)
        db.session.commit()
        return
