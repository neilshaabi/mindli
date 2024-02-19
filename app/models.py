from datetime import date
from enum import Enum
from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


class UserRole(Enum):
    CLIENT = "client"
    THERAPIST = "therapist"

class DeliveryMethod(Enum):
    INPERSON = "in-person"
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(254), index=True, unique=True
    )
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    date_joined: so.Mapped[date] = so.mapped_column(sa.Date)
    role: so.Mapped[UserRole] = so.mapped_column(sa.Enum(UserRole))
    verified: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)

    therapist: so.Mapped[Optional["Therapist"]] = so.relationship(
        back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User({self.id}: {self.email}>"


therapist_specialisation = sa.Table(
    "therapist_specialisation",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("specialisation_id", sa.ForeignKey("specialisation.id"), primary_key=True),
)

therapist_intervention = sa.Table(
    "therapist_intervention",
    db.Model.metadata,
    sa.Column("therapist_id", sa.ForeignKey("therapist.id"), primary_key=True),
    sa.Column("intervention_id", sa.ForeignKey("intervention.id"), primary_key=True),
)


class Therapist(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    
    # TODO
    # country: so.Mapped[str] = so.mapped_column(sa.String(50))
    # languages: so.Mapped[str] = so.mapped_column(sa.String(50))
    # location: so.Mapped[str]
    # session_fees: 
    delivery_methods: so.Mapped[str] = so.mapped_column(sa.Enum(DeliveryMethod))

    user: so.Mapped["User"] = so.relationship(back_populates="therapist")
    specialisations: so.Mapped[List["Specialisation"]] = so.relationship(
        secondary=therapist_specialisation, back_populates="therapists"
    )
    interventions: so.Mapped[List["Intervention"]] = so.relationship(
        secondary=therapist_intervention, back_populates="therapists"
    )


class Specialisation(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)
    
    therapists: so.Mapped[List[Therapist]] = so.relationship(
        secondary=therapist_specialisation, back_populates="specialisations"
    )

class Intervention(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), unique=True)
    
    therapists: so.Mapped[List[Therapist]] = so.relationship(
        secondary=therapist_intervention, back_populates="interventions"
    )


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
        ),
    ]
    db.session.add_all(users)
    db.session.commit()
    return