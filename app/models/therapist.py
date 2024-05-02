import random
from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.constants import COUNTRIES, EXAMPLE_THERAPIST_EMAIL
from app.models import SeedableMixin
from app.models.enums import UserRole
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.title import Title
from app.models.user import User


class Therapist(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    years_of_experience: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    qualifications: so.Mapped[str] = so.mapped_column(sa.Text)
    registrations: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    country: so.Mapped[str] = so.mapped_column(sa.String(50))
    location: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    link: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    stripe_account_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))

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
    appointments: so.Mapped[List["Appointment"]] = so.relationship(
        back_populates="therapist",
    )
    treatment_plans: so.Mapped[List["TreatmentPlan"]] = so.relationship(
        back_populates="therapist",
    )

    @property
    def is_current_user(self) -> bool:
        return current_user.id == self.user.id

    @property
    def onboarding_complete(self) -> bool:
        return (
            self and self.user.gender and self.titles and self.active_appointment_types
        )

    @property
    def active_appointment_types(self) -> List["AppointmentType"]:
        return [at for at in self.appointment_types if at.active]

    @property
    def clients(self) -> List["Client"]:
        return [appointment.client for appointment in self.appointments]

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        # Fetch titles, languages, issues, interventions from the database
        titles = db.session.execute(db.select(Title)).scalars().all()
        languages = db.session.execute(db.select(Language)).scalars().all()
        issues = db.session.execute(db.select(Issue)).scalars().all()
        interventions = db.session.execute(db.select(Intervention)).scalars().all()

        # Insert example therapist for development purposes
        example_therapist_user = db.session.execute(
            db.select(User).filter_by(email=EXAMPLE_THERAPIST_EMAIL)
        ).scalar_one()
        example_therapist = Therapist(
            user_id=example_therapist_user.id,
            years_of_experience=3,
            country="Singapore",
            location="22 Eng Hoon St, Singapore 169772",
            qualifications="Master of Psychology, NUS",
            registrations="Singapore Psychological Society (SPS)",
            link=fake.url(),
            titles=titles,
            languages=[
                db.session.execute(
                    db.select(Language).filter_by(name="English")
                ).scalar_one()
            ],
            specialisations=random.sample(
                issues, random.randint(1, min(3, len(issues)))
            ),
            interventions=random.sample(
                interventions, random.randint(1, min(3, len(interventions)))
            ),
            stripe_account_id="acct_1PBwwfFSyBYsHcUa",
        )
        db.session.add(example_therapist)

        # Fetch all other users with a role of THERAPIST
        therapist_users = (
            db.session.execute(
                db.select(User).where(
                    User.role == UserRole.THERAPIST,
                    User.email != EXAMPLE_THERAPIST_EMAIL,
                )
            )
            .scalars()
            .all()
        )

        for user in therapist_users:
            # Randomly select associated data from the fetched lists
            num_titles = random.randint(0, min(3, len(titles)))
            if num_titles == 0:
                num_titles = 1
            random_titles = random.sample(titles, num_titles)

            random_languages = random.sample(
                languages, random.randint(1, min(3, len(languages)))
            )
            random_issues = random.sample(
                issues, random.randint(1, min(3, len(issues)))
            )
            random_interventions = random.sample(
                interventions, random.randint(1, min(3, len(interventions)))
            )

            fake_therapist = Therapist(
                user_id=user.id,
                years_of_experience=random.randint(1, 20),
                country=random.choice(COUNTRIES),
                location=fake.address(),
                qualifications="Example qualification",
                registrations=fake.sentence(nb_words=4),
                link=fake.url(),
                titles=random_titles,
                languages=random_languages,
                specialisations=random_issues,
                interventions=random_interventions,
            )
            db.session.add(fake_therapist)

        db.session.commit()
        return
