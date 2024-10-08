import sqlalchemy as sa

from app import db

client_issue = sa.Table(
    "client_issue",
    db.Model.metadata,
    sa.Column("client_id", sa.ForeignKey("client.id"), primary_key=True),
    sa.Column("issue_id", sa.ForeignKey("issue.id"), primary_key=True),
)

therapist_intervention = sa.Table(
    "therapist_intervention",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("intervention_id", sa.ForeignKey("intervention.id"), primary_key=True),
)

therapist_issue = sa.Table(
    "therapist_issue",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("issue_id", sa.ForeignKey("issue.id"), primary_key=True),
)

therapist_language = sa.Table(
    "therapist_language",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("language_id", sa.ForeignKey("language.id"), primary_key=True),
)

therapist_title = sa.Table(
    "therapist_title",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("title_id", sa.ForeignKey("title.id"), primary_key=True),
)

note_issue = sa.Table(
    "note_issue",
    db.Model.metadata,
    sa.Column("note_id", sa.ForeignKey("appointment_notes.id"), primary_key=True),
    sa.Column("issue_id", sa.ForeignKey("issue.id"), primary_key=True),
)

note_intervention = sa.Table(
    "note_intervention",
    db.Model.metadata,
    sa.Column("note_id", sa.ForeignKey("appointment_notes.id"), primary_key=True),
    sa.Column("intervention_id", sa.ForeignKey("intervention.id"), primary_key=True),
)

plan_issue = sa.Table(
    "plan_issue",
    db.Model.metadata,
    sa.Column("plan_id", sa.ForeignKey("treatment_plan.id"), primary_key=True),
    sa.Column("issue_id", sa.ForeignKey("issue.id"), primary_key=True),
)

plan_intervention = sa.Table(
    "plan_intervention",
    db.Model.metadata,
    sa.Column("plan_id", sa.ForeignKey("treatment_plan.id"), primary_key=True),
    sa.Column("intervention_id", sa.ForeignKey("intervention.id"), primary_key=True),
)
