from datetime import date
from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app import db


class Client(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    date_of_birth: so.Mapped[date] = so.mapped_column(sa.Date)
    occupation: so.Mapped[str] = so.mapped_column(sa.String(50))
    address: so.Mapped[str] = so.mapped_column(sa.String(255))
    phone: so.Mapped[str] = so.mapped_column(sa.String(20))
    emergency_contact_name: so.Mapped[str] = so.mapped_column(sa.String(100))
    emergency_contact_phone: so.Mapped[str] = so.mapped_column(sa.String(20))
    referral_source: so.Mapped[str] = so.mapped_column(sa.String(100))

    user: so.Mapped["User"] = so.relationship(back_populates="client")
    issues: so.Mapped[List["Issue"]] = so.relationship(
        secondary="client_issue", back_populates="clients"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        pass
