from datetime import date
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from app import db
from app.models import SeedableMixin
from app.models.enums import UserRole


class User(UserMixin, SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(254), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(255))
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    date_joined: so.Mapped[date] = so.mapped_column(sa.Date)
    role: so.Mapped["UserRole"] = so.mapped_column(sa.Enum(UserRole))
    verified: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    photo_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    timezone: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(50)
    )  # IANA Time Zone Database name
    currency: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(3)
    )  # ISO 4217 currency code

    client: so.Mapped[Optional["Client"]] = so.relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    therapist: so.Mapped[Optional["Therapist"]] = so.relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        FAKE_PASSWORD = "ValidPassword1"

        FAKE_USER_CLIENT = User(
            email="client@example.com".lower(),
            password_hash=generate_password_hash(FAKE_PASSWORD),
            first_name="John",
            last_name="Smith",
            date_joined=date.today(),
            role=UserRole.CLIENT,
            verified=True,
            active=True,
        )

        FAKE_USER_THERAPIST = User(
            email="therapist@example.com".lower(),
            password_hash=generate_password_hash(FAKE_PASSWORD),
            first_name="Alice",
            last_name="Gray",
            date_joined=date.today(),
            role=UserRole.THERAPIST,
            verified=True,
            active=True,
        )

        fake_users = [FAKE_USER_CLIENT, FAKE_USER_THERAPIST]
        db.session.add_all(fake_users)
        db.session.commit()
        return
