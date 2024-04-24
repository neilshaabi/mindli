from datetime import datetime

from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required

from app import db
from app.forms.appointments import BookAppointmentForm, UpdateAppointmentForm
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, EmailSubject, PaymentStatus, UserRole
from app.models.therapist import Therapist
from app.models.user import User
from app.utils.decorators import client_required, therapist_required
from app.utils.mail import EmailMessage
from app.views.stripe import create_checkout_session

bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@bp.route("/", methods=["GET"])
@login_required
def index():
    
    # Dynamically choose the filter criteria depending on user's role
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

    # Render the page with the appointment forms
    return render_template(
        "appointments.html",
        appointments=appointments,
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
    update_appointment_form = UpdateAppointmentForm(
        id="update-appointment-form",
        endpoint=url_for(
            "appointments.update",
            appointment_id=appointment_id,
        ),
        role=current_user.role,
        obj=appointment,
    )

    # Render the page with the appointment details and forms
    return render_template(
        "appointment.html",
        appointment=appointment,
        update_appointment_form=update_appointment_form,
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
        flash("Therapist not found")
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
        flash("An error occurred while creating the Stripe checkout session")
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
    # Determine which function to call based on role
    if current_user.role == UserRole.THERAPIST:
        return update_therapist(appointment_id)
    elif current_user.role == UserRole.CLIENT:
        return update_client(appointment_id)


@therapist_required
def update_therapist(appointment_id: int) -> Response:
    # Fetch appointment with this ID
    appointment: Appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Redirect if appointment does not belong to this therapist
    if not appointment or current_user.id != appointment.therapist.user_id:
        flash("You do not have permission to perform this action", "error")
        return redirect(url_for("appointments.index"))

    form = UpdateAppointmentForm(role=current_user.role, obj=appointment)

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    new_status = AppointmentStatus[form.action.data]

    # Do nothing if status has not changed
    if appointment.appointment_status == new_status:
        return jsonify({"success": True})

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
        flash("Appointment rescheduled , client notified", "success")

    # COMPLETED - do nothing
    elif new_status == AppointmentStatus.COMPLETED:
        flash("Appointment marked as completed", "success")
        pass

    # CANCELLED - notify client
    elif new_status == AppointmentStatus.CANCELLED:
        send_appointment_update_email(
            appointment=appointment,
            recipient=appointment.client.user,
            subject=EmailSubject.APPOINTMENT_CANCELLED,
        )
        flash("Appointment cancelled , client notified", "success")

    # NO SHOW - notify client
    elif new_status == AppointmentStatus.NO_SHOW:
        send_appointment_update_email(
            appointment=appointment,
            recipient=appointment.client.user,
            subject=EmailSubject.APPOINTMENT_NO_SHOW_CLIENT,
        )
        flash("Appointment marked as a No Show , client notified", "success")

    else:
        return jsonify(
            {"success": False, "errors": {"action": "Invalid action selected"}}
        )

    # Update the appointment status with form data
    appointment.appointment_status = new_status
    db.session.commit()

    # Redirect to appointment page
    return jsonify(
        {
            "success": True,
            "url": url_for("appointments.appointment", appointment_id=appointment.id),
        }
    )


@client_required
def update_client(appointment_id: int) -> Response:
    # Fetch appointment with this ID
    appointment: Appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Redirect if appointment does not belong to this client
    if not appointment or current_user.id != appointment.client.user_id:
        flash("You do not have permission to perform this action", "error")
        return redirect(url_for("appointments.index"))

    form = UpdateAppointmentForm(role=current_user.role, obj=appointment)

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    new_status = AppointmentStatus[form.action.data]

    # Do nothing if status has not changed
    if appointment.appointment_status == new_status:
        return jsonify({"success": True})

    # RESCHEDULED - notify therapist and update appointment time
    if new_status == AppointmentStatus.RESCHEDULED:
        send_appointment_update_email(
            appointment=appointment,
            recipient=appointment.therapist.user,
            subject=EmailSubject.APPOINTMENT_RESCHEDULED,
        )
        appointment.time = datetime.combine(form.new_date.data, form.new_time.data)
        flash("Appointment rescheduled , therapist notified", "success")

    # CANCELLED - notify therapist
    elif new_status == AppointmentStatus.CANCELLED:
        send_appointment_update_email(
            appointment=appointment,
            recipient=appointment.therapist.user,
            subject=EmailSubject.APPOINTMENT_CANCELLED,
        )
        flash("Appointment cancelled , therapist notified", "success")

    else:
        return jsonify(
            {"success": False, "errors": {"action": "Invalid action selected"}}
        )

    appointment.appointment_status = new_status
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "url": url_for("appointments.appointment", appointment_id=appointment.id),
        }
    )


def send_appointment_update_email(
    appointment: Appointment, recipient: User, subject: EmailSubject
) -> None:
    email = EmailMessage(
        recipient=recipient,
        subject=subject,
        context={"appointment": appointment},
        url_params={"appointment_id": appointment.id},
    )
    email.send()
    return
