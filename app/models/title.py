from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin


class Title(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)

    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_title", back_populates="titles"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        title_names = ["Therapist", "Psychologist", "Coach"]
        titles = [Title(name=title) for title in title_names]
        db.session.add_all(titles)
        db.session.commit()
        return
