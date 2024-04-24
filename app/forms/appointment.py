from wtforms import DateField, SubmitField, TimeField
from wtforms.validators import DataRequired, Optional

from app.forms import CustomFlaskForm, CustomSelectField
from app.models.enums import AppointmentStatus


class TherapistUpdateAppointmentForm(CustomFlaskForm):
    action = CustomSelectField(
        "Action",
        choices=[
            ("", "Select action"),
        ],
        default="",
        validators=[DataRequired()],
    )
    new_date = DateField("Date", format="%Y-%m-%d", validators=[Optional()])
    new_time = TimeField("Time", validators=[Optional()])
    submit = SubmitField("Update")

    def __init__(self, *args, **kwargs):
        super(TherapistUpdateAppointmentForm, self).__init__(*args, **kwargs)

        appointment = kwargs.get("obj")

        if appointment:
            # Define all possible choices for actions
            all_action_choices = [
                (AppointmentStatus.CONFIRMED.name, "Confirm"),
                (AppointmentStatus.RESCHEDULED.name, "Reschedule"),
                (AppointmentStatus.COMPLETED.name, "Completed"),
                (AppointmentStatus.CANCELLED.name, "Cancel"),
                (AppointmentStatus.NO_SHOW.name, "No Show"),
            ]

            # Filter out the choice that matches the current status
            filtered_actions = [
                action
                for action in all_action_choices
                if action[0] != appointment.appointment_status.name
            ]
            self.action.choices.extend(filtered_actions)
        return
