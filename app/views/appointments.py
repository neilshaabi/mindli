from datetime import datetime

from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from app import db
from app.forms.appointments import (
    AppointmentNotesForm,
    BookAppointmentForm,
    FilterAppointmentsForm,
    TherapyExerciseForm,
    UpdateAppointmentForm,
)
from app.models.appointment import Appointment
from app.models.appointment_notes import AppointmentNotes
from app.models.client import Client
from app.models.enums import (
    AppointmentStatus,
    EmailSubject,
    PaymentStatus,
    TherapyMode,
    TherapyType,
    UserRole,
)
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
    filters_from_session = session.get("appointment_filters", {})
    if "start_date" in filters_from_session and filters_from_session["start_date"]:
        filters_from_session["start_date"] = convert_str_to_date(
            filters_from_session["start_date"]
        )
    if "end_date" in filters_from_session and filters_from_session["end_date"]:
        filters_from_session["end_date"] = convert_str_to_date(
            filters_from_session["end_date"]
        )

    # Initialise filter form with fields prepopulated from session
    filter_form = FilterAppointmentsForm(
        id="filter-appointments",
        endpoint=url_for("appointments.filter"),
        data=filters_from_session,
    )

    # Render the page with the appointment forms
    return render_template(
        "appointments.html", appointments=appointments, filter_form=filter_form
    )


@bp.route("/<int:appointment_id>", methods=["GET"])
@login_required
def appointment(appointment_id: int) -> Response:
    # Fetch appointment with this ID
    appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one_or_none()

    # Redirect to appointments page if appointment not found
    if not appointment or appointment.this_user.id != current_user.id:
        flash("You do not have permission to view this appointment", "error")
        return redirect(url_for("appointments.index"))

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

    # Create appointment notes form for therapist only
    if current_user.role == UserRole.THERAPIST:
        notes_form = AppointmentNotesForm(
            id="appointment-notes-form",
            endpoint=url_for("appointments.notes", appointment_id=appointment_id),
            obj=appointment.notes,
        )
    else:
        # Do not give other users access to appointment notes
        notes_form = None

    # Render the page with the appointment details and forms
    return render_template(
        "appointment.html",
        appointment=appointment,
        update_form=update_form,
        notes_form=notes_form,
        exercise_form=exercise_form,
    )


@bp.route("/create/<int:therapist_id>", methods=["GET"])
@login_required
@client_required
def view_book_appointment(therapist_id: int) -> Response:
    # Fetch therapist with this ID
    therapist = db.session.execute(
        db.select(Therapist).filter_by(id=therapist_id)
    ).scalar_one_or_none()

    # Redirect if therapist not found
    if not therapist:
        flash("Therapist not found", "error")
        return redirect(url_for("main.index"))

    # Initialise form for client to book an appointment with this therapist
    form = BookAppointmentForm(
        obj=therapist,
        id="book_appointment",
        endpoint=url_for(
            "appointments.process_book_appointment", therapist_id=therapist_id
        ),
    )

    return render_template("book_appointment.html", therapist=therapist, form=form)


@bp.route("/create/<int:therapist_id>", methods=["POST"])
@login_required
@client_required
def process_book_appointment(therapist_id: int) -> Response:
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
    checkout_session_url = create_checkout_session(new_appointment)
    if not checkout_session_url:
        flash("An error occurred while creating the Stripe checkout session", "error")
        return jsonify(
            {
                "success": False,
                "errors": {
                    "appointment_type": ["Failed to create Stripe checkout session"]
                },
            }
        )
    else:
        return jsonify({"success": True, "url": checkout_session_url})


@bp.route("/update/<int:appointment_id>", methods=["POST"])
@login_required
def update(appointment_id: int) -> Response:
    # Fetch appointment with this ID
    appointment: Appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Redirect if appointment does not belong to this user
    if not appointment or appointment.this_user.id != current_user.id:
        flash("You do not have permission to perform this action", "error")
        return redirect(
            url_for("appointments.appointment", appointment_id=appointment_id)
        )

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
    flashed_message_category = "success"

    # Handle actions differently depending on role of current user
    if current_user.role == UserRole.THERAPIST:
        # CONFIRMED - notify client
        if new_status == AppointmentStatus.CONFIRMED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.client.user,
                subject=EmailSubject.APPOINTMENT_CONFIRMED_CLIENT,
            )

        # RESCHEDULED - notify client and update appointment time
        elif new_status == AppointmentStatus.RESCHEDULED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.client.user,
                subject=EmailSubject.APPOINTMENT_RESCHEDULED,
            )
            appointment.time = datetime.combine(form.new_date.data, form.new_time.data)
            flashed_message_text = "Appointment rescheduled, client notified"

        # COMPLETED - do nothing
        elif new_status == AppointmentStatus.COMPLETED:
            flashed_message_text = "Appointment marked as completed"

        # CANCELLED - notify client
        elif new_status == AppointmentStatus.CANCELLED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.client.user,
                subject=EmailSubject.APPOINTMENT_CANCELLED,
            )
            flashed_message_text = "Appointment cancelled, client notified"

        # NO SHOW - notify client
        elif new_status == AppointmentStatus.NO_SHOW:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.client.user,
                subject=EmailSubject.APPOINTMENT_NO_SHOW_CLIENT,
            )
            flashed_message_text = "Appointment marked as a No Show, client notified"

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

        # CANCELLED - notify therapist
        elif new_status == AppointmentStatus.CANCELLED:
            send_appointment_update_email(
                appointment=appointment,
                recipient=appointment.therapist.user,
                subject=EmailSubject.APPOINTMENT_CANCELLED,
            )
            flashed_message_text = "Appointment cancelled, therapist notified"

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
    appointment: Appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Redirect if appointment does not belong to this therapist
    if not appointment or current_user.id != appointment.therapist.user_id:
        flash("You do not have permission to perform this action", "error")
        return redirect(
            url_for("appointments.appointment", appointment_id=appointment_id)
        )

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
    db.session.commit()

    # Update data in association tables
    form.issues.update_association_data(
        parent=appointment.notes, child=Issue, children="issues"
    )
    form.interventions.update_association_data(
        parent=appointment.notes, child=Intervention, children="interventions"
    )

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
    appointment: Appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Redirect if appointment does not belong to this user
    if not appointment or current_user.id != appointment.this_user.id:
        flash("You do not have permission to perform this action", "error")
        return redirect(
            url_for("appointments.appointment", appointment_id=appointment_id)
        )

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
    filter_form = FilterAppointmentsForm()

    # Invalid form submission - return errors
    if not filter_form.validate_on_submit():
        return jsonify({"success": False, "errors": filter_form.errors})

    # Handle submissions via different submit buttons separately
    submit_action = request.form["submit"]

    if submit_action == "filter":
        # Store filter settings in the session
        session["appointment_filters"] = {
            "name": filter_form.name.data,
            "start_date": filter_form.start_date.data,
            "end_date": filter_form.end_date.data,
            "appointment_status": filter_form.appointment_status.data,
            "payment_status": filter_form.payment_status.data,
            "therapy_type": filter_form.therapy_type.data,
            "therapy_mode": filter_form.therapy_mode.data,
            "duration": filter_form.duration.data,
            "fee_currency": filter_form.fee_currency.data,
            "notes": filter_form.notes.data,
            "issues": filter_form.issues.data,
            "interventions": filter_form.interventions.data,
            "exercise_title": filter_form.exercise_title.data,
            "exercise_description": filter_form.exercise_description.data,
            "exercise_completed": filter_form.exercise_completed.data,
        }
        # # Create a dictionary to store the filters
        # filters = {}
        # for field_name, field_object in filter_form._fields.items():
        #     filters[field_name] = field_object.data
        # session["appointment_filters"] = filters

        # Begin building the base query
        query = db.select(Appointment)

        # Apply filters by extending the query with conditions for each filter
        if filter_form.name.data:
            search_term = f"%{filter_form.name.data.lower()}%"
            query = (
                query.join(Client)
                .join(User)
                .where(
                    func.lower(User.first_name + " " + User.last_name).like(search_term)
                )
            )

        if filter_form.start_date.data:
            query = query.where(Appointment.time >= filter_form.start_date.data)

        if filter_form.end_date.data:
            query = query.where(Appointment.time <= filter_form.end_date.data)

        if filter_form.appointment_status.data:
            appointment_status = AppointmentStatus[filter_form.appointment_status.data]
            query = query.where(Appointment.appointment_status == appointment_status)

        if filter_form.payment_status.data:
            payment_status = PaymentStatus[filter_form.payment_status.data]
            query = query.where(Appointment.payment_status == payment_status)

        if filter_form.therapy_type.data:
            types = [TherapyType[t] for t in filter_form.therapy_type.data]
            type_conditions = [
                Appointment.appointment_type.has(therapy_type=t) for t in types
            ]
            query = query.filter(or_(*type_conditions))

        if filter_form.therapy_mode.data:
            modes = [TherapyMode[mode] for mode in filter_form.therapy_mode.data]
            mode_conditions = [
                Appointment.appointment_type.has(therapy_mode=mode) for mode in modes
            ]
            query = query.filter(or_(*mode_conditions))

        if filter_form.duration.data:
            query = query.where(
                Appointment.appointment_type.has(duration=filter_form.duration.data)
            )

        if filter_form.fee_currency.data:
            query = query.where(
                Appointment.appointment_type.has(
                    fee_currency=filter_form.fee_currency.data
                )
            )

        if filter_form.notes.data:
            search_term = f"%{filter_form.notes.data.lower()}%"
            query = query.join(AppointmentNotes).where(
                func.lower(AppointmentNotes.text).like(search_term)
            )

        if filter_form.issues.data:
            query = (
                query.join(Appointment.notes)
                .join(AppointmentNotes.issues)
                .where(Issue.id.in_(filter_form.issues.data))
            )

        if filter_form.interventions.data:
            query = (
                query.join(Appointment.notes)
                .join(AppointmentNotes.interventions)
                .where(Intervention.id.in_(filter_form.interventions.data))
            )

        if filter_form.exercise_title.data:
            search_term = f"%{filter_form.exercise_title.data.lower()}%"
            query = query.join(TherapyExercise).where(
                func.lower(TherapyExercise.title).like(search_term)
            )

        if filter_form.exercise_description.data:
            search_term = f"%{filter_form.exercise_description.data.lower()}%"
            query = query.join(TherapyExercise).where(
                func.lower(TherapyExercise.description).like(search_term)
            )

        if filter_form.exercise_completed.data:
            completed_status = filter_form.exercise_completed.data == "True"
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
            {% from "_macros.html" import appointment_row %}
            {% for appointment in appointments %}
                {{ appointment_row(appointment) }}
            {% endfor %}
            """,
            appointments=filtered_appointments,
        )

        filter_count_html = render_template_string(
            "{{ appointments|length }} appointments found",
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

    elif submit_action == "reset_filters":
        # Clear filter settings from the session if they exist
        session.pop("appointment_filters", None)
        return jsonify({"success": True, "url": url_for("appointments.index")})
