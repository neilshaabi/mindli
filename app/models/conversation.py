from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.constants import EXAMPLE_THERAPIST_EMAIL
from app.models import SeedableMixin
from app.models.enums import UserRole
from app.models.user import User


class Conversation(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("user.id"), index=True
    )
    client_user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("user.id"), index=True
    )
    messages: so.Mapped[List["Message"]] = so.relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )

    therapist_user: so.Mapped["User"] = so.relationship(
        back_populates="conversations_as_therapist", foreign_keys=[therapist_user_id]
    )
    client_user: so.Mapped["User"] = so.relationship(
        back_populates="conversations_as_client", foreign_keys=[client_user_id]
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        # Create conversations between example therapist and clients
        example_therapist_user = db.session.execute(
            db.select(User).filter_by(email=EXAMPLE_THERAPIST_EMAIL)
        ).scalar_one()

        client_users = (
            db.session.execute(db.select(User).filter_by(role=UserRole.CLIENT))
            .scalars()
            .all()
        )

        conversations = [
            Conversation(
                therapist_user_id=example_therapist_user.id,
                client_user_id=client_user.id,
            )
            for client_user in client_users
        ]

        db.session.add_all(conversations)
        db.session.commit()
        return
