from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.enums import SessionFormat


class SessionFormatModel(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    session_format: so.Mapped[str] = so.mapped_column(
        sa.Enum(SessionFormat), unique=True
    )

    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_format", back_populates="session_formats"
    )
