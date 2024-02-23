from datetime import date, time
from enum import Enum, unique
from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


@unique
class UserRole(Enum):
    CLIENT = "client"
    THERAPIST = "therapist"


@unique
class SessionFormat(Enum):
    FACE = "Face to Face"
    AUDIO = "Audio Call"
    VIDEO = "Video Call"


@unique
class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    NON_BINARY = "Non-Binary"


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


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(254), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(255))
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    date_joined: so.Mapped[date] = so.mapped_column(sa.Date)
    role: so.Mapped["UserRole"] = so.mapped_column(sa.Enum(UserRole))
    verified: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    gender: so.Mapped[Optional["Gender"]] = so.mapped_column(sa.Enum(Gender))
    photo_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    timezone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))  # IANA Time Zone Database name
    currency: so.Mapped[Optional[str]] = so.mapped_column(sa.String(3))  # ISO 4217 currency code
    
    client: so.Mapped[Optional["Client"]] = so.relationship(back_populates="user")
    therapist: so.Mapped[Optional["Therapist"]] = so.relationship(back_populates="user")


class Client(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), index=True)
    preferred_gender: so.Mapped[Optional["Gender"]] = so.mapped_column(sa.Enum(Gender))
    preferred_language: so.Mapped[Optional["Language"]] = so.mapped_column(sa.Enum(Gender))
    
    user: so.Mapped["User"] = so.relationship(back_populates="client")
    issues: so.Mapped[List["Issue"]] = so.relationship(secondary=client_issue, back_populates="clients")


class Therapist(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    country: so.Mapped[str] = so.mapped_column(sa.String(50))
    affilitation: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    bio: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    link: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    location: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    registrations: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    qualifications: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    years_of_experience: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)
    
    user: so.Mapped["User"] = so.relationship(back_populates="therapist")
    languages: so.Mapped[List["Language"]] = so.relationship(secondary=therapist_language, back_populates="therapists")
    specialisations: so.Mapped[List["Issue"]] = so.relationship(secondary=therapist_issue, back_populates="therapists")
    interventions: so.Mapped[List["Intervention"]] = so.relationship(secondary=therapist_intervention, back_populates="therapists")
    session_types: so.Mapped[List["SessionType"]] = so.relationship(back_populates="therapist")
    availabilities: so.Mapped[List["Availability"]] = so.relationship(back_populates="therapist")
    unavailabilities: so.Mapped[List["Unavailability"]] = so.relationship(back_populates="therapist")


class Language(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)
    iso639_1: so.Mapped[Optional[str]] = so.mapped_column(sa.String(2), unique=True)  # ISO 639-1 two-letter code
    iso639_2: so.Mapped[Optional[str]] = so.mapped_column(sa.String(3), unique=True)  # ISO 639-2 three-letter code
    
    therapists: so.Mapped[List["Therapist"]] = so.relationship(secondary=therapist_language, back_populates="languages")


class Issue(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)
    
    clients: so.Mapped[List["Client"]] = so.relationship(secondary=client_issue, back_populates="issues")
    therapists: so.Mapped[List["Therapist"]] = so.relationship(secondary=therapist_issue, back_populates="specialisations")


class Intervention(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)
    
    therapists: so.Mapped[List["Therapist"]] = so.relationship(secondary=therapist_intervention, back_populates="interventions")


class SessionType(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("therapist.id"), index=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255))  # e.g. "Initial Consultation"
    session_duration: so.Mapped[int] = so.mapped_column(sa.Integer)  # In minutes
    fee_amount: so.Mapped[float] = so.mapped_column(sa.Float)
    fee_currency: so.Mapped[str] = so.mapped_column(sa.String(3))
    session_format: so.Mapped[Optional[SessionFormat]] = so.mapped_column(sa.Enum(SessionFormat))
    notes: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    
    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="session_types")


class Availability(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("therapist.id"), index=True)
    day_of_week: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)  # 0=Monday, 6=Sunday, None for specific dates
    start_time: so.Mapped[Optional[time]] = so.mapped_column(sa.Time)
    end_time: so.Mapped[Optional[time]] = so.mapped_column(sa.Time)
    specific_date: so.Mapped[Optional[date]] = so.mapped_column(sa.Date)  # For non-recurring availability
    
    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="availabilities")


class Unavailability(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("therapist.id"), index=True)
    start_date: so.Mapped[date] = so.mapped_column(sa.Date)
    end_date: so.Mapped[date] = so.mapped_column(sa.Date)
    reason: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    
    therapist: so.Mapped["Therapist"] = so.relationship(back_populates="unavailabilities")


def insertDummyData() -> None:
    users: List[User] = [
        User(
            email="client@example.com",
            password_hash=generate_password_hash("password"),
            first_name="John",
            last_name="Smith",
            date_joined=date.today(),
            role=UserRole.CLIENT,
            verified=True,
            active=True,
            gender=Gender.MALE,
        ),
        User(
            email="therapist@example.com",
            password_hash=generate_password_hash("password"),
            first_name="Jane",
            last_name="Doe",
            date_joined=date.today(),
            role=UserRole.THERAPIST,
            verified=False,
            active=True,
            gender=Gender.FEMALE,
        ),
    ]
    db.session.add_all(users)
    db.session.commit()
    return
