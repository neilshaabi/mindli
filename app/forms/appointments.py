from wtforms import (
    DateField,
    DecimalField,
    HiddenField,
    IntegerField,
    SelectField,
    SubmitField,
    TimeField,
)
from wtforms.validators import DataRequired, NumberRange

from app.constants import CURRENCIES
from app.forms import CustomFlaskForm, CustomSelectField
from app.models.enums import TherapyMode, TherapyType
from app.utils.validators import LocationRequired


class AppointmentTypeForm(CustomFlaskForm):
    therapy_type = CustomSelectField(
        "Type",
        choices=[("", "Select type")]
        + [(choice.name, choice.value) for choice in TherapyType],
        default="",
        validators=[DataRequired()],
    )
    therapy_mode = CustomSelectField(
        "Mode",
        choices=[("", "Select mode")]
        + [(choice.name, choice.value) for choice in TherapyMode],
        default="",
        validators=[DataRequired(), LocationRequired()],
    )
    duration = IntegerField(
        "Duration (minutes)",
        validators=[DataRequired(), NumberRange(min=1)],
    )
    fee_amount = DecimalField(
        "Fee",
        validators=[DataRequired(), NumberRange(min=0.01)],
    )
    fee_currency = SelectField(
        "Currency",
        choices=[("", "Select currency")]
        + [(currency, currency) for currency in CURRENCIES],
        validators=[DataRequired()],
    )

    def __init__(self, *args, **kwargs):
        super(AppointmentTypeForm, self).__init__(*args, **kwargs)
        appointment_type = kwargs.get("obj")
        if appointment_type:
            self.therapy_type.preselect_choices(appointment_type.therapy_type)
            self.therapy_mode.preselect_choices(appointment_type.therapy_mode)
        return


class DeleteAppointmentTypeForm(CustomFlaskForm):
    appointment_type_id = HiddenField(
        "Appointment type ID", validators=[DataRequired()]
    )
    submit = SubmitField("Delete")


class BookAppointmentForm(CustomFlaskForm):
    appointment_type = CustomSelectField(
        "Appointment type",
        choices=[("", "Select appointment type")],
        default="",
        validators=[DataRequired()],
    )
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
    submit = SubmitField("Book Appointment")

    def __init__(self, *args, **kwargs):
        super(BookAppointmentForm, self).__init__(*args, **kwargs)
        therapist = kwargs.get("obj")
        self.appointment_type.choices.extend(
            [
                (
                    at.id,
                    (
                        f"{at.therapy_type.value}, {at.therapy_mode.value} ({at.duration} minutes) - {at.fee_amount} {at.fee_currency}"
                    ),
                )
                for at in therapist.appointment_types
            ]
        )
        return
