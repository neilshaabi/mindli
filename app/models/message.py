from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.user import User


class Message(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    conversation_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("conversation.id"), index=True
    )
    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    content: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime)

    conversation: so.Mapped["Conversation"] = so.relationship(back_populates="messages")
    author: so.Mapped["User"] = so.relationship(back_populates="messages")
