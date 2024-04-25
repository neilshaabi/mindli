from wtforms import (DecimalField, HiddenField, IntegerField, SelectField,
                     SubmitField)
from wtforms.validators import DataRequired, NumberRange

from app.constants import CURRENCIES
from app.forms import CustomFlaskForm, CustomSelectField
from app.models.enums import TherapyMode, TherapyType
from app.utils.validators import LocationRequired, MinimumFeeAmount


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
        validators=[DataRequired(), NumberRange(min=0.01), MinimumFeeAmount()],
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
