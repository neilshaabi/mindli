from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class Language(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)
    alpha_2: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(2), unique=True
    )  # ISO 639-1 two-letter code
    alpha_3: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(3), unique=True
    )  # ISO 639-2 three-letter code

    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_language", back_populates="languages"
    )
