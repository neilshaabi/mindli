from wtforms import DateField, SubmitField, TimeField
from wtforms.validators import DataRequired, Optional

from app.forms import CustomFlaskForm, CustomSelectField
from app.models.enums import AppointmentStatus, UserRole


class UpdateAppointmentForm(CustomFlaskForm):
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

    def __init__(self, role: UserRole, *args, **kwargs):
        super(UpdateAppointmentForm, self).__init__(*args, **kwargs)

        appointment = kwargs.get("obj")

        # Define choices for actions depending on user role
        if role == UserRole.THERAPIST:
            action_choices = [
                (AppointmentStatus.CONFIRMED.name, "Confirm"),
                (AppointmentStatus.RESCHEDULED.name, "Reschedule"),
                (AppointmentStatus.COMPLETED.name, "Completed"),
                (AppointmentStatus.CANCELLED.name, "Cancel"),
                (AppointmentStatus.NO_SHOW.name, "No Show"),
            ]
        elif role == UserRole.CLIENT:
            action_choices = [
                (AppointmentStatus.RESCHEDULED.name, "Reschedule"),
                (AppointmentStatus.CANCELLED.name, "Cancel"),
            ]

        # Filter out the choice that matches the current status
        filtered_actions = [
            choice
            for choice in action_choices
            if choice[0] != appointment.appointment_status.name
        ]
        self.action.choices.extend(filtered_actions)
        return
