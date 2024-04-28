import random
from datetime import date
from typing import List

from flask_login import current_user
import phonenumbers
import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models.enums import Occupation, ReferralSource, UserRole
from app.models.issue import Issue
from app.models.therapist import Therapist
from app.models.user import User


class Client(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), index=True
    )
    date_of_birth: so.Mapped[date] = so.mapped_column(sa.Date)
    occupation: so.Mapped[Occupation] = so.mapped_column(sa.Enum(Occupation))
    address: so.Mapped[str] = so.mapped_column(sa.String(255))
    phone: so.Mapped[str] = so.mapped_column(sa.String(20))
    emergency_contact_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    emergency_contact_phone: so.Mapped[str] = so.mapped_column(sa.String(20))
    referral_source: so.Mapped[ReferralSource] = so.mapped_column(
        sa.Enum(ReferralSource)
    )

    user: so.Mapped["User"] = so.relationship(back_populates="client")
    issues: so.Mapped[List["Issue"]] = so.relationship(
        secondary="client_issue", back_populates="clients"
    )
    appointments: so.Mapped[List["Appointment"]] = so.relationship(
        back_populates="client",
    )

    @property
    def is_current_user(self) -> bool:
        return current_user.id == self.user.id

    @property
    def age(self) -> int:
        if not self.date_of_birth:
            return None
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    def get_appointments_with_therapist(
        self, therapist: Therapist
    ) -> List["Appointment"]:
        from app.models.appointment import Appointment

        return (
            db.session.execute(
                db.select(Appointment).filter_by(
                    client_id=self.id, therapist_id=therapist.id
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        def generate_valid_phone_number(country_code="US"):
            while True:
                try:
                    fake_phone_number = phonenumbers.parse(
                        fake.phone_number(), country_code
                    )
                    if phonenumbers.is_valid_number(fake_phone_number):
                        return phonenumbers.format_number(
                            fake_phone_number, phonenumbers.PhoneNumberFormat.E164
                        )
                except phonenumbers.NumberParseException:
                    continue

        issues = db.session.execute(db.select(Issue)).scalars().all()

        # Fetch all users with a role of CLIENT
        client_users = (
            db.session.execute(db.select(User).where(User.role == UserRole.CLIENT))
            .scalars()
            .all()
        )

        for user in client_users:
            fake_client = Client(
                user_id=user.id,
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=65),
                occupation=random.choice(list(Occupation)),
                address=fake.address(),
                phone=generate_valid_phone_number(),
                emergency_contact_name=fake.name(),
                emergency_contact_phone=generate_valid_phone_number(),
                referral_source=random.choice(list(ReferralSource)),
                issues=random.sample(issues, random.randint(1, min(3, len(issues)))),
            )
            db.session.add(fake_client)

        db.session.commit()
