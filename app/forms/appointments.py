from wtforms import (BooleanField, DateField, IntegerField, SelectField,
                     StringField, SubmitField, TextAreaField, TimeField)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.constants import CURRENCIES
from app.forms import (CustomFlaskForm, CustomSelectField,
                       CustomSelectMultipleField)
from app.models.enums import (AppointmentStatus, PaymentStatus, TherapyMode,
                              TherapyType, UserRole)
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
    submit = SubmitField("Proceed to Payment")

    def __init__(self, *args, **kwargs):
        super(BookAppointmentForm, self).__init__(*args, **kwargs)
        therapist = kwargs.get("obj")
        self.appointment_type.choices.extend(
            [
                (
                    at.id,
                    (
                        f"{at.therapy_type.value}, {at.therapy_mode.value} ({at.duration} minutes) - {at.fee_currency}{at.fee_amount}"
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
        self.action.choices.extend(action_choices)
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


class FilterAppointmentsForm(CustomFlaskForm):
    name = StringField("Name", validators=[Optional()])

    # Appointment specific filters
    start_date = DateField("Start Date", validators=[Optional()])
    end_date = DateField("End Date", validators=[Optional()])
    appointment_status = CustomSelectField(
        "Status",
        choices=[("", "Select status")],
        validators=[Optional()],
    )
    payment_status = CustomSelectField(
        "Payment",
        choices=[("", "Select status")],
        validators=[Optional()],
    )

    # AppointmentType specific filters
    therapy_type = CustomSelectMultipleField(
        "Therapy type",
        choices=[("", "Any")],
        validators=[Optional()],
    )
    therapy_mode = CustomSelectMultipleField(
        "Mode",
        choices=[("", "Any")],
        validators=[Optional()],
    )
    duration = IntegerField("Duration (minutes)", validators=[Optional()])
    fee_currency = SelectField(
        "Currency",
        choices=[("", "Select currency")]
        + [(currency, currency) for currency in CURRENCIES],
        validators=[Optional()],
    )

    # AppointmentNotes specific filters
    notes = StringField("Search notes", validators=[Optional()])
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

    # TherapyExercise specific filters
    exercise_title = StringField("Exercise title", validators=[Optional()])
    exercise_description = StringField("Description", validators=[Optional()])
    exercise_completed = SelectField(
        "Completed",
        choices=[("", "Any"), ("True", "Completed"), ("False", "Incomplete")],
        validators=[Optional()],
    )

    # Submit buttons
    submit_filter = SubmitField("Filter Appointments", render_kw={"name": "filter"})
    submit_reset_filters = SubmitField(
        "Reset Filters", render_kw={"name": "reset_filters"}
    )

    def __init__(self, *args, **kwargs):
        super(FilterAppointmentsForm, self).__init__(*args, **kwargs)
        self.appointment_status.populate_choices(AppointmentStatus)
        self.payment_status.populate_choices(PaymentStatus)

        self.therapy_type.populate_choices(TherapyType)
        self.therapy_mode.populate_choices(TherapyMode)

        self.interventions.populate_choices(Intervention)
        self.issues.populate_choices(Issue)
        return
