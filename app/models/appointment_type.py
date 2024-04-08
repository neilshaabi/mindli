import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app.models.enums import TherapyMode, TherapyType


class AppointmentType(db.Model):
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
