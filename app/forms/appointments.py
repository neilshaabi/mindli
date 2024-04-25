from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.forms import CustomFlaskForm, CustomSelectField, CustomSelectMultipleField
from app.models.enums import AppointmentStatus, UserRole
from app.models.intervention import Intervention
from app.models.issue import Issue


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
                for at in therapist.active_appointment_types
            ]
        )
        return


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


class AppointmentNotesForm(CustomFlaskForm):
    text = TextAreaField("Notes", validators=[DataRequired()])
    issues = CustomSelectMultipleField(
        "Issues discussed",
        validators=[Optional()],
        coerce=int,
    )
    interventions = CustomSelectMultipleField(
        "Interventions applied",
        validators=[Optional()],
        coerce=int,
    )
    efficacy = IntegerField(
        "Efficacy (1-5)", validators=[Optional(), NumberRange(min=1, max=5)]
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(AppointmentNotesForm, self).__init__(*args, **kwargs)

        self.issues.populate_choices(Issue)
        self.interventions.populate_choices(Intervention)

        appointment_note = kwargs.get("obj")
        if appointment_note:
            self.issues.preselect_choices(appointment_note.issues)
            self.interventions.preselect_choices(appointment_note.interventions)
        return


class TherapyExerciseForm(CustomFlaskForm):
    title = StringField("Title", validators=[Length(max=255)])
    description = TextAreaField("Description", validators=[Optional()])
    client_response = TextAreaField("Client response", validators=[Optional()])
    completed = BooleanField(
        "Mark as completed",
        validators=[],
        default=False,
    )
    submit = SubmitField("Save")

    def __init__(self, role: UserRole, *args, **kwargs):
        super(TherapyExerciseForm, self).__init__(*args, **kwargs)

        # Disable fields depending on role
        if role == UserRole.THERAPIST:
            self.client_response.render_kw = {"disabled": "disabled"}
        elif role == UserRole.CLIENT:
            self.title.render_kw = {"disabled": "disabled"}
            self.description.render_kw = {"disabled": "disabled"}
        return
