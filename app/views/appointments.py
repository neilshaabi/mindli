from datetime import datetime

from flask import (Blueprint, Response, abort, jsonify, render_template,
                   render_template_string, request, session, url_for)
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from app import db
from app.forms.appointments import (AppointmentNotesForm, BookAppointmentForm,
                                    FilterAppointmentsForm,
                                    TherapyExerciseForm, UpdateAppointmentForm)
from app.models.appointment import Appointment
from app.models.appointment_notes import AppointmentNotes
from app.models.client import Client
from app.models.enums import (AppointmentStatus, EmailSubject, PaymentStatus,
                              TherapyMode, TherapyType, UserRole)
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.therapist import Therapist
from app.models.therapy_exercise import TherapyExercise
from app.models.user import User
from app.utils.decorators import client_required, therapist_required
from app.utils.formatters import convert_str_to_date, get_flashed_message_html
from app.utils.mail import send_appointment_update_email
from app.views.stripe import create_checkout_session

bp = Blueprint("appointments", __name__, url_prefix="/appointments")
FILTERS_SESSION_KEY = "appointment_filters"


@bp.route("/", methods=["GET"])
@login_required
def index():
    # Dynamically choose the criteria to filter appointments depending on user's role
    if current_user.role == UserRole.THERAPIST:
        filter_criteria = Appointment.therapist_id == current_user.therapist.id
    elif current_user.role == UserRole.CLIENT:
        filter_criteria = Appointment.client_id == current_user.client.id

    # Fetch all of the the current user's appointments ordered by the most recent
    appointments = (
        db.session.execute(
            db.select(Appointment)
            .filter(filter_criteria)
            .order_by(Appointment.time.desc())
        )
        .scalars()
        .all()
    )

    # Convert dates stored as str in session to initialise filter form
    filters = session.get(FILTERS_SESSION_KEY, {})
    if "start_date" in filters and filters["start_date"]:
        filters["start_date"] = convert_str_to_date(filters["start_date"])
    if "end_date" in filters and filters["end_date"]:
        filters["end_date"] = convert_str_to_date(filters["end_date"])

    # Initialise filter form with fields prepopulated from session
    filter_form = FilterAppointmentsForm(
        id="filter-appointments",
        endpoint=url_for("appointments.filter"),
        data=filters,
    )

    # Render the page with the appointment forms
    return render_template(
        "appointments.html",
        active_page="appointments",
        appointments=appointments,
        filter_form=filter_form,
    )


@bp.route("/<int:appointment_id>", methods=["GET"])
@login_required
def appointment(appointment_id: int) -> Response:
    # Fetch appointment with this ID
    appointment = db.get_or_404(Appointment, appointment_id)

    # Current user is not in this appointment
    if appointment.this_user.id != current_user.id:
        abort(403)

    # Initialise form to update appointment, passing role to distinguish allowed actions
    update_form = UpdateAppointmentForm(
        id="update-appointment-form",
        endpoint=url_for(
            "appointments.update",
            appointment_id=appointment_id,
        ),
        role=current_user.role,
    )

    # Create form to set and update a therapy exercise
    exercise_form = TherapyExerciseForm(
        id="therapy-exercise-form",
        endpoint=url_for("appointments.exercise", appointment_id=appointment_id),
        role=current_user.role,
        obj=appointment.exercise,
    )

    # Do not give other users access to appointment notes
    notes_form = None

    # Create appointment notes form for therapist only
    if current_user.role == UserRole.THERAPIST:
        notes_form = AppointmentNotesForm(
            id="appointment-notes-form",
            endpoint=url_for("appointments.notes", appointment_id=appointment_id),
            obj=appointment.notes,
        )

    # Render the page with the appointment details and forms
    return render_template(
        "appointment.html",
        active_page="appointments",
        appointment=appointment,
        update_form=update_form,
        notes_form=notes_form,
        exercise_form=exercise_form,
    )


@bp.route("/create/<int:therapist_id>", methods=["POST"])
@login_required
@client_required
def create(therapist_id: int) -> Response:
    # Fetch therapist with this ID to initialise form correctly
    therapist = db.session.execute(
        db.select(Therapist).filter_by(id=therapist_id)
    ).scalar_one()

    form = BookAppointmentForm(obj=therapist)

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Add new appointment with pending payment in database
    new_appointment = Appointment(
        therapist_id=therapist_id,
        client_id=current_user.client.id,
        appointment_type_id=form.appointment_type.data,
        time=datetime.combine(form.date.data, form.time.data),
        appointment_status=AppointmentStatus.SCHEDULED,
        payment_status=PaymentStatus.PENDING,
    )
    db.session.add(new_appointment)
    db.session.commit()

    # Redirect the client to Stripe Checkout
    if not therapist.stripe_account_id:
        return jsonify(
            {
                "success": True,
                "url": url_for(
                    "appointments.appointment", appointment_id=appointment.id
                ),
                "flashed_message_html": get_flashed_message_html(
                    message="Appointment scheduled, awaiting payment and confirmation",
                    category="info",
                ),
            }
        )

    checkout_session_url = create_checkout_session(new_appointment)

    if not checkout_session_url:
        return jsonify(
            {
                "success": False,
                "flashed_message_html": get_flashed_message_html(
                    message="Failed to initiate payment via Stripe, please contact therapist",
                    category="error",
                ),
            }
        )
    else:
        return jsonify(
            {
                "success": False,
                "url": checkout_session_url,
            }
        )


@bp.route("/update/<int:appointment_id>", methods=["POST"])
@login_required
def update(appointment_id: int) -> Response:
    # Fetch appointment with this ID
    appointment = db.get_or_404(Appointment, appointment_id)

    # Current user is not in this appointment
    if appointment.this_user.id != current_user.id:
        abort(403)

    form = UpdateAppointmentForm(role=current_user.role)

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    new_status = AppointmentStatus[form.action.data]

    # Do nothing if status has not changed
    if appointment.appointment_status == new_status:
        return jsonify({"success": True})

    # Handle missing date and time fields for rescheduled
    if new_status == AppointmentStatus.RESCHEDULED:
        datetime_errors = {}
        if form.new_date.data is None:
            datetime_errors["new_date"] = ["New date is required."]
        if form.new_time.data is None:
            datetime_errors["new_time"] = ["New time is required."]

        if datetime_errors:
            return jsonify({"success": False, "errors": datetime_errors})

    flashed_message_text = None
    flashed_message_category = None

    # Handle actions differently depending on role of current user
    if current_user.role == UserRole.THERAPIST:
        # CONFIRMED - notify client
        if new_status == AppointmentStatus.CONFIRMED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.client.user,
                subject=EmailSubject.APPOINTMENT_CONFIRMED_CLIENT,
            )
            flashed_message_text = "Appointment confirmed, client notified"
            flashed_message_category = "success"

        # RESCHEDULED - notify client and update appointment time
        elif new_status == AppointmentStatus.RESCHEDULED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.client.user,
                subject=EmailSubject.APPOINTMENT_RESCHEDULED,
            )
            appointment.time = datetime.combine(form.new_date.data, form.new_time.data)
            flashed_message_text = "Appointment rescheduled, client notified"
            flashed_message_category = "success"

        # COMPLETED - do nothing
        elif new_status == AppointmentStatus.COMPLETED:
            flashed_message_text = "Appointment recorded as completed"
            flashed_message_category = "success"

        # CANCELLED - notify client
        elif new_status == AppointmentStatus.CANCELLED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.client.user,
                subject=EmailSubject.APPOINTMENT_CANCELLED,
            )
            flashed_message_text = "Appointment cancelled, client notified"
            flashed_message_category = "warning"

        # NO SHOW - notify client
        elif new_status == AppointmentStatus.NO_SHOW:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.client.user,
                subject=EmailSubject.APPOINTMENT_NO_SHOW_CLIENT,
            )
            flashed_message_text = "Appointment recorded as a No Show, client notified"
            flashed_message_category = "warning"

        else:
            return jsonify(
                {"success": False, "errors": {"action": "Invalid action selected"}}
            )

    elif current_user.role == UserRole.CLIENT:
        # RESCHEDULED - notify therapist and update appointment time
        if new_status == AppointmentStatus.RESCHEDULED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.therapist.user,
                subject=EmailSubject.APPOINTMENT_RESCHEDULED,
            )
            appointment.time = datetime.combine(form.new_date.data, form.new_time.data)
            flashed_message_text = "Appointment rescheduled, therapist notified"
            flashed_message_category = "success"

        # CANCELLED - notify therapist
        elif new_status == AppointmentStatus.CANCELLED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.therapist.user,
                subject=EmailSubject.APPOINTMENT_CANCELLED,
            )
            flashed_message_text = "Appointment cancelled, therapist notified"
            flashed_message_category = "warning"

        else:
            return jsonify(
                {"success": False, "errors": {"action": "Invalid action selected"}}
            )

    # Update the appointment status with form data
    appointment.appointment_status = new_status
    db.session.commit()

    # Construct template string to updated appointment status via AJAX
    status_tag_html = render_template_string(
        """
        {% from '_macros.html' import tag %}
        {{ tag(label=label, status=status, with_icon=True, additional_class='tag-lg') }}
    """,
        label=appointment.appointment_status.value,
        status=appointment.appointment_status.name,
    )

    # Redirect to appointment page
    return jsonify(
        {
            "success": True,
            "update_targets": {"status-tag": status_tag_html},
            "flashed_message_html": get_flashed_message_html(
                flashed_message_text, flashed_message_category
            ),
        }
    )


@bp.route("/<int:appointment_id>/notes", methods=["POST"])
@login_required
@therapist_required
def notes(appointment_id: int) -> Response:
    # Fetch appointment with this ID
    appointment = db.get_or_404(Appointment, appointment_id)

    # Current user is not the therapist for the appointment
    if not appointment.therapist.is_current_user:
        abort(403)

    form = AppointmentNotesForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Create new appointment notes if one does not exist
    if not appointment.notes:
        appointment.notes = AppointmentNotes(appointment_id=appointment.id)
        db.session.add(appointment.notes)

    # Update appointment notes with form data
    appointment.notes.text = form.text.data
    appointment.notes.efficacy = form.efficacy.data
    appointment.notes.last_updated = datetime.now()
    db.session.flush()

    # Update data in association tables
    form.issues.update_association_data(
        parent=appointment.notes, child=Issue, children="issues"
    )
    form.interventions.update_association_data(
        parent=appointment.notes, child=Intervention, children="interventions"
    )
    db.session.commit()

    # Flash message using AJAX
    return jsonify(
        {
            "success": True,
            "flashed_message_html": get_flashed_message_html(
                "Appointment notes updated", "success"
            ),
        }
    )


@bp.route("/<int:appointment_id>/exercise", methods=["POST"])
@login_required
def exercise(appointment_id: int) -> Response:
    # Fetch appointment with this ID
    appointment = db.get_or_404(Appointment, appointment_id)

    # Current user is not in this appointment
    if appointment.this_user.id != current_user.id:
        abort(403)

    form = TherapyExerciseForm(role=current_user.role)

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Create new exercise if one does not exist and current user is therapist
    if not appointment.exercise and current_user.role == UserRole.THERAPIST:
        appointment.exercise = TherapyExercise(
            appointment_id=appointment.id,
            title=form.title.data,
            description=form.description.data,
            client_response=None,
            completed=False,
        )
        db.session.add(appointment.exercise)

    # Update exercise with form data as therapist
    elif current_user.role == UserRole.THERAPIST:
        appointment.exercise.title = form.title.data
        appointment.exercise.description = form.description.data
        appointment.exercise.completed = form.completed.data

    # Update exercise with form data as client
    elif current_user.role == UserRole.CLIENT:
        appointment.exercise.client_response = form.client_response.data
        appointment.exercise.completed = form.completed.data

    db.session.commit()

    # Construct template strings to updated completion status via AJAX
    status = "Completed" if appointment.exercise.completed else "Incomplete"
    completion_tag_html = render_template_string(
        """
        {% from '_macros.html' import tag %}
        {{ tag(label=status, status=status, with_icon=True) }}
    """,
        status=status,
    )
    completion_tag_sm_html = render_template_string(
        """
        {% from '_macros.html' import tag %}
        {{ tag(status=status, with_icon=True, additional_class='tag-sm') }}
    """,
        status=status,
    )

    # Flash message using AJAX and update completion status
    return jsonify(
        {
            "success": True,
            "update_targets": {
                "completion-tag": completion_tag_html,
                "completion-tag-sm": completion_tag_sm_html,
            },
            "flashed_message_html": get_flashed_message_html(
                "Therapy exercise updated", "success"
            ),
        }
    )


@bp.route("/filter", methods=["POST"])
@login_required
def filter():
    form = FilterAppointmentsForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Handle submissions via different submit buttons separately
    submit_action = request.form["submit"]

    # Store filter settings in the session
    if submit_action == "filter":
        form.store_data_in_session(FILTERS_SESSION_KEY)

        # Begin building the base query
        query = db.select(Appointment)

        # Apply filters by extending the query with conditions for each filter
        if form.name.data:
            search_term = f"%{form.name.data.lower()}%"
            query = (
                query.join(Client)
                .join(User)
                .where(
                    func.lower(User.first_name + " " + User.last_name).like(search_term)
                )
            )

        if form.start_date.data:
            query = query.where(Appointment.time >= form.start_date.data)

        if form.end_date.data:
            query = query.where(Appointment.time <= form.end_date.data)

        if form.appointment_status.data:
            appointment_status = AppointmentStatus[form.appointment_status.data]
            query = query.where(Appointment.appointment_status == appointment_status)

        if form.payment_status.data:
            payment_status = PaymentStatus[form.payment_status.data]
            query = query.where(Appointment.payment_status == payment_status)

        if form.therapy_type.data:
            types = [TherapyType[t] for t in form.therapy_type.data]
            type_conditions = [
                Appointment.appointment_type.has(therapy_type=t) for t in types
            ]
            query = query.filter(or_(*type_conditions))

        if form.therapy_mode.data:
            modes = [TherapyMode[mode] for mode in form.therapy_mode.data]
            mode_conditions = [
                Appointment.appointment_type.has(therapy_mode=mode) for mode in modes
            ]
            query = query.filter(or_(*mode_conditions))

        if form.duration.data:
            query = query.where(
                Appointment.appointment_type.has(duration=form.duration.data)
            )

        if form.fee_currency.data:
            query = query.where(
                Appointment.appointment_type.has(fee_currency=form.fee_currency.data)
            )

        if form.notes.data:
            search_term = f"%{form.notes.data.lower()}%"
            query = query.join(AppointmentNotes).where(
                func.lower(AppointmentNotes.text).like(search_term)
            )

        if form.issues.data:
            query = (
                query.join(Appointment.notes)
                .join(AppointmentNotes.issues)
                .where(Issue.id.in_(form.issues.data))
            )

        if form.interventions.data:
            query = (
                query.join(Appointment.notes)
                .join(AppointmentNotes.interventions)
                .where(Intervention.id.in_(form.interventions.data))
            )

        if form.exercise_title.data:
            search_term = f"%{form.exercise_title.data.lower()}%"
            query = query.join(TherapyExercise).where(
                func.lower(TherapyExercise.title).like(search_term)
            )

        if form.exercise_description.data:
            search_term = f"%{form.exercise_description.data.lower()}%"
            query = query.join(TherapyExercise).where(
                func.lower(TherapyExercise.description).like(search_term)
            )

        if form.exercise_completed.data:
            completed_status = form.exercise_completed.data == "True"
            query = query.join(TherapyExercise).where(
                TherapyExercise.completed == completed_status
            )

        # Execute query to filter appointments
        filtered_appointments = (
            db.session.execute(query.order_by(Appointment.time.desc())).scalars().all()
        )

        # Construct template string to insert updated appointments via AJAX
        appointments_html = render_template_string(
            """
            {% from "_macros.html" import appointment_row with context %}
            {% for appointment in appointments %}
                {{ appointment_row(appointment) }}
            {% endfor %}
            """,
            appointments=filtered_appointments,
        )

        filter_count_html = render_template_string(
            "{{ appointments|length if appointments else 0}} appointments found",
            appointments=filtered_appointments,
        )

        return jsonify(
            {
                "success": True,
                "update_targets": {
                    "appointment-rows": appointments_html,
                    "filter-count": filter_count_html,
                },
            }
        )

    # Clear filter settings from the session if they exist
    elif submit_action == "reset_filters":
        session.pop(FILTERS_SESSION_KEY, None)
        return jsonify({"success": True, "url": url_for("appointments.index")})
