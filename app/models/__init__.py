import sqlalchemy as sa

from app import db

from .availability import Availability
from .client import Client
from .enums import Gender, SessionFormat, UserRole
from .intervention import Intervention
from .issue import Issue
from .language import Language
from .session_type import SessionType
from .therapist import Therapist
from .unavailability import Unavailability
from .user import User

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

therapist_format = sa.Table(
    "therapist_format",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("session_format", sa.Enum(SessionFormat), primary_key=True),
)

therapist_issue = sa.Table(
    "therapist_issue",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("issue_id", sa.ForeignKey("issue.id"), primary_key=True),
)

therapist_intervention = sa.Table(
    "therapist_intervention",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("intervention_id", sa.ForeignKey("intervention.id"), primary_key=True),
)
