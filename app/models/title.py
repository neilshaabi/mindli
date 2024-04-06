from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin
from app.models.enums import ProfessionalTitle


class Title(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)

    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_title", back_populates="titles"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        titles = [Title(name=title.value) for title in ProfessionalTitle]
        db.session.add_all(titles)
        db.session.commit()
        return
