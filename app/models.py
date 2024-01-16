from datetime import date
from enum import Enum
from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


class UserRole(Enum):
    """Enumeration for the user role (client or therapist)"""

    CLIENT = "client"
    THERAPIST = "therapist"


class User(UserMixin, db.Model):
    """Model of a User stored in the database"""

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

    def __repr__(self) -> str:
        """
        Returns a string representing a user with
        their id and email address, used by print()
        """
        return f"<User {self.id}: {self.email}>"


def resetDatabase() -> None:
    """Insert dummy data into database"""

    # Reset database
    db.drop_all()
    db.create_all()

    # Sample list of users
    users: List[User] = [
        User(
            email="neilshaabi@gmail.com",
            password_hash=generate_password_hash("n"),
            first_name="Neil",
            last_name="Shaabi",
            date_joined=date.today(),
            role=UserRole.THERAPIST,
            verified=True,
            active=True,
        ),
        User(
            email="neil.shaabi@warwick.ac.uk",
            password_hash=generate_password_hash("n"),
            first_name="John",
            last_name="Doe",
            date_joined=date.today(),
            role=UserRole.CLIENT,
            verified=False,  # Assuming the client's email is not yet verified
            active=True,
        ),
    ]
    db.session.add_all(users)
    db.session.commit()
    return
