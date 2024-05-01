import random
from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.constants import EXAMPLE_CLIENT_EMAIL, EXAMPLE_THERAPIST_EMAIL
from app.models import SeedableMixin
from app.models.enums import UserRole
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.user import User


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
    interventions_description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    goals: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    medication: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    last_updated: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=datetime.now()
    )

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

    @property
    def this_user(self) -> User:
        if current_user.role == UserRole.THERAPIST:
            return self.therapist.user
        elif current_user.role == UserRole.CLIENT:
            return self.client.user

    @property
    def other_user(self) -> User:
        if current_user.role == UserRole.THERAPIST:
            return self.client.user
        elif current_user.role == UserRole.CLIENT:
            return self.therapist.user

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        # Fetch example therapist and client
        example_therapist_user = db.session.execute(
            db.select(User).filter_by(email=EXAMPLE_THERAPIST_EMAIL)
        ).scalar_one()

        example_client_user = db.session.execute(
            db.select(User).filter_by(email=EXAMPLE_CLIENT_EMAIL)
        ).scalar_one()

        issues = db.session.execute(db.select(Issue)).scalars().all()
        interventions = db.session.execute(db.select(Intervention)).scalars().all()

        random_issues = random.sample(issues, random.randint(1, min(3, len(issues))))
        random_interventions = random.sample(
            interventions, random.randint(1, min(3, len(interventions)))
        )

        # Create treatment plan between example therapist and client
        example_treatment_plan = TreatmentPlan(
            therapist_id=example_therapist_user.therapist.id,
            client_id=example_client_user.client.id,
            issues_description="The client experiences symptoms of anxiety and depression, including persistent feelings of worry, restlessness, and sadness, impacting daily functioning.",
            interventions_description="Combination of Cognitive-behavioral therapy (CBT) techniques, such as identifying and challenging negative thought patterns and mindfulness exercises to promote present-moment awareness and stress reduction.",
            goals="The primary goals of the treatment plan are to alleviate anxiety symptoms, enhance mood regulation, and improve overall well-being. Specific objectives include:1. Developing coping strategies for managing stressors, 2. Increasing self-awareness, 3. Fostering a sense of empowerment.",
            medication="Selective serotonin reuptake inhibitor (SSRI) medication to address symptoms of depression.",
            issues=random_issues,
            interventions=random_interventions,
        )
        db.session.add(example_treatment_plan)
        db.session.commit()
        return
