from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin


class TreatmentPlan(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id"), index=True
    )
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id", ondelete="CASCADE"), index=True
    )
    client_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("client.id"), index=True)
    issues_description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    intervention_description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    goals: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    medication: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    client_can_view: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)

    therapist: so.Mapped["Therapist"] = so.relationship(
        back_populates="treatment_plans"
    )
    client: so.Mapped["Client"] = so.relationship(back_populates="treatment_plans")
    issues: so.Mapped[List["Issue"]] = so.relationship(
        secondary="plan_issue", back_populates="treatment_plans"
    )
    interventions: so.Mapped[List["Intervention"]] = so.relationship(
        secondary="plan_intervention", back_populates="treatment_plans"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        return NotImplemented
