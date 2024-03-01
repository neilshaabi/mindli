from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models.enums import SessionFormat


class SessionFormatModel(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)

    clients: so.Mapped[List["Client"]] = so.relationship(
        secondary="client_format", back_populates="session_formats"
    )
    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_format", back_populates="session_formats"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        session_formats = [
            SessionFormatModel(name=session_format.value)
            for session_format in SessionFormat
        ]
        db.session.add_all(session_formats)
        db.session.commit()
        return
