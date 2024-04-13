import random
from datetime import datetime, timedelta

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.constants import EXAMPLE_THERAPIST_EMAIL
from app.models.conversation import Conversation
from app.models.user import User


class Message(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    conversation_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("conversation.id"), index=True
    )
    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime)

    conversation: so.Mapped["Conversation"] = so.relationship(back_populates="messages")
    author: so.Mapped["User"] = so.relationship(back_populates="messages")

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        # Fetch example therapist
        example_therapist_user = db.session.execute(
            db.select(User).filter_by(email=EXAMPLE_THERAPIST_EMAIL)
        ).scalar_one()

        conversations = (
            db.session.execute(
                db.select(Conversation).filter_by(
                    therapist_user_id=example_therapist_user.id
                )
            )
            .scalars()
            .all()
        )

        messages = []

        # Insert 10 random messages in order of datetime in conversations with example therapist,
        for conversation in conversations:
            last_timestamp = fake.past_datetime(start_date="-2y", tzinfo=None)
            for _ in range(10):
                timestamp = last_timestamp + timedelta(minutes=random.randint(1, 120))
                last_timestamp = timestamp
                messages.append(
                    Message(
                        conversation_id=conversation.id,
                        author_id=random.choice(
                            [example_therapist_user.id, conversation.client_user.id]
                        ),
                        content=fake.sentence(nb_words=random.randint(5, 20)),
                        timestamp=timestamp,
                    )
                )
        db.session.add_all(messages)
        db.session.commit()
        return
