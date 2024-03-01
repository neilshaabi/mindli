from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin


class Issue(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)

    clients: so.Mapped[List["Client"]] = so.relationship(
        secondary="client_issue", back_populates="issues"
    )
    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_issue", back_populates="specialisations"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        issue_names = [
            "Anxiety",
            "Depression",
            "Stress",
        ]
        issues = [Issue(name=issue_name) for issue_name in issue_names]
        db.session.add_all(issues)
        db.session.commit()
        return
