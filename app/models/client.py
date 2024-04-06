from typing import List, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.enums import Gender


class Client(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    preferred_gender: so.Mapped[Optional["Gender"]] = so.mapped_column(sa.Enum(Gender))
    preferred_language_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey("language.id")
    )

    user: so.Mapped["User"] = so.relationship(back_populates="client")
    preferred_language: so.Mapped[Optional["Language"]] = so.relationship(
        back_populates="clients"
    )
    issues: so.Mapped[List["Issue"]] = so.relationship(
        secondary="client_issue", back_populates="clients"
    )