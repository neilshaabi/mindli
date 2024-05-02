import random

import sqlalchemy as sa
import sqlalchemy.orm as so
from faker import Faker
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.constants import CURRENCIES, EXAMPLE_THERAPIST_EMAIL
from app.models import SeedableMixin
from app.models.enums import TherapyMode, TherapyType
from app.models.therapist import Therapist
from app.models.user import User


class AppointmentType(SeedableMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    therapist_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("therapist.id", ondelete="CASCADE"), index=True
    )
    therapy_type: so.Mapped["TherapyType"] = so.mapped_column(sa.Enum(TherapyType))
    therapy_mode: so.Mapped["TherapyMode"] = so.mapped_column(sa.Enum(TherapyMode))
    duration: so.Mapped[int] = so.mapped_column(sa.Integer)
    fee_amount: so.Mapped[float] = so.mapped_column(sa.Float)
    fee_currency: so.Mapped[str] = so.mapped_column(sa.String(3))
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)

    therapist: so.Mapped["Therapist"] = so.relationship(
        back_populates="appointment_types"
    )
    appointments: so.Mapped["Appointment"] = so.relationship(
        back_populates="appointment_type"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy, fake: Faker) -> None:
        # Create fixed appointment type for example therapist
        example_therapist_user = db.session.execute(
            db.select(User).filter_by(email=EXAMPLE_THERAPIST_EMAIL)
        ).scalar_one()

        appointment_type = AppointmentType(
            therapist_id=example_therapist_user.therapist.id,
            therapy_type=TherapyType.INDIVIDUAL,
            therapy_mode=TherapyMode.IN_PERSON,
            duration=random.choice([30, 45, 60, 90]),
            fee_amount=100,
            fee_currency="SGD",
        )
        db.session.add(appointment_type)

        # Fetch all therapists
        therapists = db.session.execute(db.select(Therapist)).scalars().all()

        # Create random appointment types for each therapist
        for therapist in therapists:
            for _ in range(random.randint(2, 5)):
                appointment_type = AppointmentType(
                    therapist_id=therapist.id,
                    therapy_type=random.choice(list(TherapyType)),
                    therapy_mode=random.choice(list(TherapyMode)),
                    duration=random.choice([30, 45, 60, 90]),
                    fee_amount=round(random.uniform(50.0, 200.0) / 10) * 10,
                    fee_currency=random.choice(CURRENCIES),
                )
                db.session.add(appointment_type)

        db.session.commit()
        return
