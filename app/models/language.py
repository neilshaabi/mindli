from typing import List, Optional

import pycountry
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin


class Language(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)
    alpha_2: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(2), unique=True
    )  # ISO 639-1 two-letter code
    alpha_3: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(3), unique=True
    )  # ISO 639-2 three-letter code

    clients: so.Mapped[List["Client"]] = so.relationship(
        back_populates="preferred_language"
    )
    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_language", back_populates="languages"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        languages = [
            Language(
                name=language.name,
                alpha_2=getattr(language, "alpha_2", None),
                alpha_3=getattr(language, "alpha_3", None),
            )
            for language in pycountry.languages
            if language.type == "L"
        ]
        db.session.add_all(languages)
        db.session.commit()
        return
