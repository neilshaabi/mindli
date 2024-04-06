import sqlalchemy as sa

from app import db

client_issue = sa.Table(
    "client_issue",
    db.Model.metadata,
    sa.Column("client_id", sa.ForeignKey("client.id"), primary_key=True),
    sa.Column("issue_id", sa.ForeignKey("issue.id"), primary_key=True),
)

therapist_language = sa.Table(
    "therapist_language",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("language_id", sa.ForeignKey("language.id"), primary_key=True),
)

therapist_issue = sa.Table(
    "therapist_issue",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("issue_id", sa.ForeignKey("issue.id"), primary_key=True),
)
