from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.forms.appointment import UpdateAppointmentForm
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, EmailSubject, UserRole
from app.models.user import User
from app.utils.decorators import client_required, therapist_required
from app.utils.mail import EmailMessage

bp = Blueprint("appointment", __name__, url_prefix="/appointment")


@bp.route("/<int:appointment_id>", methods=["GET"])
@login_required
def view_appointment(appointment_id):
    # Determine next endpoints based on current user's role
    if current_user.role == UserRole.THERAPIST:
        redirect_endpoint = "appointments.appointments_therapist"
        post_endpoint = "appointment.update_appointment_therapist"
    elif current_user.role == UserRole.CLIENT:
        redirect_endpoint = "appointments.appointments_client"
        post_endpoint = "appointment.update_appointment_client"

    # Fetch appointment with this ID
    appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one_or_none()

    # Redirect to appointments page if appointment not found
    if not appointment or appointment.this_user.id != current_user.id:
        flash("You do not have permission to view this appointment", "error")
        return redirect(url_for(redirect_endpoint))

    # Initialise form to update appointment, using role to distinguish
    update_appointment_form = UpdateAppointmentForm(
        id="update-appointment-form",
        endpoint=url_for(
            post_endpoint,
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


@bp.route("/update/<int:appointment_id>/therapist", methods=["POST"])
@login_required
@therapist_required
def update_appointment_therapist(appointment_id):
    # Fetch appointment with this ID
    appointment: Appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Redirect if appointment does not belong to this therapist
    if not appointment or current_user.id != appointment.therapist.user_id:
        flash("You do not have permission to perform this action", "error")
        return redirect(url_for("appointments.appointments_therapist"))

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
        flash("Appointment rescheduled and client notified", "success")

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
        flash("Appointment cancelled and client notified", "success")

    # NO SHOW - notify client
    elif new_status == AppointmentStatus.NO_SHOW:
        send_appointment_update_email(
            appointment=appointment,
            recipient=appointment.client.user,
            subject=EmailSubject.APPOINTMENT_NO_SHOW_CLIENT,
        )
        flash("Appointment marked as a No Show and client notified", "success")

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
            "url": url_for(
                "appointment.view_appointment", appointment_id=appointment.id
            ),
        }
    )


@bp.route("/update/<int:appointment_id>/client", methods=["POST"])
@login_required
@client_required
def update_appointment_client(appointment_id):
    # Fetch appointment with this ID
    appointment: Appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Redirect if appointment does not belong to this client
    if not appointment or current_user.id != appointment.client.user_id:
        flash("You do not have permission to perform this action", "error")
        return redirect(url_for("appointments.appointments_client"))

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
        flash("Appointment rescheduled and therpaist notified", "success")

    # CANCELLED - notify therapist
    elif new_status == AppointmentStatus.CANCELLED:
        send_appointment_update_email(
            appointment=appointment,
            recipient=appointment.therapist.user,
            subject=EmailSubject.APPOINTMENT_CANCELLED,
        )
        flash("Appointment cancelled and therapist notified", "success")

    else:
        return jsonify(
            {"success": False, "errors": {"action": "Invalid action selected"}}
        )

    appointment.appointment_status = new_status
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "url": url_for(
                "appointment.view_appointment", appointment_id=appointment.id
            ),
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
