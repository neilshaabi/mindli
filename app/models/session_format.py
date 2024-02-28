from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class SessionFormatModel(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)

    clients: so.Mapped[List["Client"]] = so.relationship(
        secondary="client_format", back_populates="session_formats"
    )
    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_format", back_populates="session_formats"
    )
