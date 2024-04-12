from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.user import User


class Conversation(db.Model):
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
