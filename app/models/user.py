import os
import random
from datetime import date
from typing import List, Optional

import requests
import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from app import db
from app.constants import (
    EXAMPLE_CLIENT_EMAIL,
    EXAMPLE_THERAPIST_EMAIL,
    EXAMPLE_VALID_PASSWORD,
)
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
            return self.therapist and self.therapist.onboarding_complete
        elif self.role == UserRole.CLIENT:
            return self.client and self.client.onboarding_complete
        print(f"Unhandled user role: {self.role}")
        return False

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        used_emails = set()

        def fetch_random_user_from_api(save_profile_picture: bool = True) -> dict:
            while True:
                # Fetch random user data from external API
                response = requests.get("https://randomuser.me/api/")
                data = response.json()

                # Extract user data
                user_data = data.get("results")[0]
                email = user_data.get("email")

                # Retry if email has already been used
                if email in used_emails:
                    continue

                user_data["profile_pic_filename"] = None

                if save_profile_picture:
                    # Save profile picture locally
                    profile_pic_url = user_data["picture"]["medium"]
                    profile_pic_filename = f"user_{fake.uuid4()}.jpg"
                    profile_pic_filepath = os.path.join(
                        "app", "static", "img", "profile_pictures", profile_pic_filename
                    )
                    with open(profile_pic_filepath, "wb") as f:
                        pic_response = requests.get(profile_pic_url)
                        f.write(pic_response.content)
                    user_data["profile_pic_filename"] = profile_pic_filename
                return user_data

        def make_random_user(role: UserRole, **kwargs) -> User:
            random_user_data = {}

            # Fetch data from external API
            if current_app.config["SEED_FROM_EXTERNAL_API"]:
                random_user_data = fetch_random_user_from_api()
                email = random_user_data["email"]
                first_name = random_user_data["name"]["first"]
                last_name = random_user_data["name"]["last"]
                profile_pic = random_user_data.get("profile_pic_filename")
                try:
                    gender = Gender[random_user_data["gender"].upper()]
                except KeyError:
                    gender = random.choice(list(Gender))

            # Generate data using faker and random
            else:
                email = fake.unique.email().lower()
                while email in used_emails:
                    email = fake.unique.email().lower()
                first_name = fake.first_name()
                last_name = fake.last_name()
                gender = random.choice(list(Gender))
                profile_pic = None

            user = User(
                email=email,
                password_hash=generate_password_hash(EXAMPLE_VALID_PASSWORD),
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                role=role,
                date_joined=fake.past_date(start_date="-1y", tzinfo=None),
                profile_picture=profile_pic,
                verified=True,
                active=True,
            )

            # Update values with kwargs if provided
            for key, value in kwargs.items():
                setattr(user, key, value)

            # Keep track of used emails to prevent duplicates
            used_emails.add(email)
            return user

        fake_users = []

        # Insert example therapist and client for development purposes
        fake_users.append(
            make_random_user(role=UserRole.THERAPIST, email=EXAMPLE_THERAPIST_EMAIL)
        )
        fake_users.append(
            make_random_user(role=UserRole.CLIENT, email=EXAMPLE_CLIENT_EMAIL)
        )
        used_emails.add(EXAMPLE_THERAPIST_EMAIL)
        used_emails.add(EXAMPLE_CLIENT_EMAIL)

        # Insert 20 fake therapists and clients (10 each)
        for _ in range(10):
            fake_users.append(make_random_user(UserRole.THERAPIST))
            fake_users.append(make_random_user(UserRole.CLIENT))

        db.session.add_all(fake_users)
        db.session.commit()
        return
