import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.models import SeedableMixin
from app.models.enums import TherapyMode, TherapyType
from app.models.therapist import Therapist


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

    therapist: so.Mapped["Therapist"] = so.relationship(
        back_populates="appointment_types"
    )

    @classmethod
    def seed(cls, db: SQLAlchemy) -> None:
        fake_therapist = db.session.execute(
            db.select(Therapist).order_by(Therapist.id)
        ).scalar_one()

        fake_appointment_type = AppointmentType(
            therapist_id=fake_therapist.id,
            therapy_type=TherapyType.INDIVIDUAL,
            therapy_mode=TherapyMode.IN_PERSON,
            duration=60,
            fee_amount=200,
            fee_currency="USD",
        )
        db.session.add(fake_appointment_type)
        db.session.commit()
        return
