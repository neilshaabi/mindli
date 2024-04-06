from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin


class Intervention(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)

    therapists: so.Mapped[List["Therapist"]] = so.relationship(
        secondary="therapist_intervention", back_populates="interventions"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        intervention_names = [
            "Acceptance and commitment therapy (ACT)",
            "Art therapy",
            "Cognitive behaviour therapy (CBT)",
            "Dialectical behaviour therapy (DBT)",
            "Emotion-focused therapy (EFT)",
            "Eye movement desensitisation and reprocessing (EMDR)",
            "Existential therapy",
            "Gestalt Therapy",
            "Hypnotherapy",
            "Integrative psychotherapy",
            "Interpersonal psychotherapy (IPT)",
            "Logotherapy",
            "Mindfulness-based cognitive therapy (MBCT)",
            "Mindfulness-based stress reduction (MBSR)",
            "Motivational Interviewing (MI)",
            "Music therapy",
            "Narrative therapy",
            "Neuro-linguistic programming (NLP)",
            "Person-Centered Therapy",
            "Play therapy",
            "Positive psychology",
            "Psychodynamic psychotherapy (PDT)",
            "Psychoeducation",
            "Rational emotive behavior therapy (REBT)",
            "Schema therapy",
            "Solution-focused brief therapy (SFBT)",
            "Systemic therapy",
            "Transpersonal psychology",
            "Transactional Analysis",
        ]
        interventions = [
            Intervention(name=intervention_name)
            for intervention_name in intervention_names
        ]
        db.session.add_all(interventions)
        db.session.commit()
        return
