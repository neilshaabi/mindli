import random
from datetime import date
from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from app import db
from app.constants import EXAMPLE_CLIENT_EMAIL, EXAMPLE_THERAPIST_EMAIL
from app.models import SeedableMixin
from app.models.enums import Gender, UserRole


class User(UserMixin, SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(255), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(255))
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    gender: so.Mapped[Optional["Gender"]] = so.mapped_column(sa.Enum(Gender))
    role: so.Mapped["UserRole"] = so.mapped_column(sa.Enum(UserRole))
    date_joined: so.Mapped[date] = so.mapped_column(sa.Date, default=date.today())
    verified: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    profile_picture: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(255), default="default.png"
    )

    client: so.Mapped[Optional["Client"]] = so.relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    therapist: so.Mapped[Optional["Therapist"]] = so.relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    conversations_as_therapist: so.Mapped[
        Optional[List["Conversation"]]
    ] = so.relationship(
        back_populates="therapist_user",
        lazy="dynamic",
        foreign_keys="Conversation.therapist_user_id",
    )
    conversations_as_client: so.Mapped[
        Optional[List["Conversation"]]
    ] = so.relationship(
        back_populates="client_user",
        lazy="dynamic",
        foreign_keys="Conversation.client_user_id",
    )
    messages: so.Mapped[Optional["Message"]] = so.relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def onboarding_complete(self) -> bool:
        if self.role == UserRole.THERAPIST:
            return self.therapist and self.therapist.onboarding_complete()
        elif self.role == UserRole.CLIENT:
            return self.user and self.client.onboarding_complete()
        print(f"Unhandled user role: {self.role}")
        return False

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        # Create a fake email that doesn't already exist in the database
        def unique_fake_email() -> str:
            fake_email = fake.unique.email().lower()
            while (
                db.session.execute(
                    db.select(User).filter_by(email=fake_email)
                ).scalar_one_or_none()
                is not None
            ):
                fake_email = fake.unique.email()
            return fake_email

        # Fake password that meets requirements to be used for all users
        fake_password_hash = generate_password_hash("ValidPassword1")

        # Insert example client for development purposes
        example_fake_user_client = User(
            email=EXAMPLE_CLIENT_EMAIL.lower(),
            password_hash=fake_password_hash,
            first_name="John",
            last_name="Smith",
            gender=Gender.MALE,
            role=UserRole.CLIENT,
            date_joined=fake.past_date(start_date="-1y", tzinfo=None),
            verified=True,
            active=True,
        )
        db.session.add(example_fake_user_client)

        # Insert example therapist for development purposes
        example_fake_user_therapist = User(
            email=EXAMPLE_THERAPIST_EMAIL.lower(),
            password_hash=fake_password_hash,
            first_name="Jane",
            last_name="Doe",
            gender=Gender.FEMALE,
            role=UserRole.THERAPIST,
            date_joined=fake.past_date(start_date="-1y", tzinfo=None),
            verified=True,
            active=True,
        )
        db.session.add(example_fake_user_therapist)

        # Insert 10 clients with fake and randomly selected data
        for _ in range(10):
            fake_user_therapist = User(
                email=unique_fake_email(),
                password_hash=fake_password_hash,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                gender=random.choice(list(Gender)),
                role=UserRole.CLIENT,
                date_joined=fake.past_date(start_date="-1y", tzinfo=None),
                verified=True,
                active=True,
            )
            db.session.add(fake_user_therapist)

        # Insert 10 therapists with fake and randomly selected data
        for _ in range(10):
            fake_user_therapist = User(
                email=unique_fake_email(),
                password_hash=fake_password_hash,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                gender=random.choice(list(Gender)),
                role=UserRole.THERAPIST,
                date_joined=fake.past_date(start_date="-1y", tzinfo=None),
                verified=True,
                active=True,
            )
            db.session.add(fake_user_therapist)

        db.session.commit()
        return
