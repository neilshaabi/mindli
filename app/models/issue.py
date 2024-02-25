from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db


class Issue(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)

    clients: so.Mapped[List["Client"]] = so.relationship(
        secondary="client_issue", back_populates="issues"
    )
    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_issue", back_populates="specialisations"
    )
