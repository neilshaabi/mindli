from datetime import date
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin

from app import db
from app.models.enums import Gender, UserRole


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(254), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(255))
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    date_joined: so.Mapped[date] = so.mapped_column(sa.Date)
    role: so.Mapped["UserRole"] = so.mapped_column(sa.Enum(UserRole))
    verified: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    gender: so.Mapped[Optional["Gender"]] = so.mapped_column(sa.Enum(Gender))
    photo_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    timezone: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(50)
    )  # IANA Time Zone Database name
    currency: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(3)
    )  # ISO 4217 currency code

    client: so.Mapped[Optional["Client"]] = so.relationship(back_populates="user")
    therapist: so.Mapped[Optional["Therapist"]] = so.relationship(back_populates="user")
