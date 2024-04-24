from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.forms.appointment import TherapistUpdateAppointmentForm
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, EmailSubject, UserRole
from app.models.user import User
from app.utils.decorators import therapist_required
from app.utils.mail import EmailMessage

bp = Blueprint("appointment", __name__, url_prefix="/appointment")


@bp.route("/<int:appointment_id>", methods=["GET"])
@login_required
def view_appointment(appointment_id):
    # TODO: REMOVE THIS VARIABLE AND REDIRECT LOGIC ONCE MERGED APPOINTMENTS ROUTE
    current_user_field = (
        "therapist" if current_user.role == UserRole.THERAPIST else "client"
    )

    # Fetch appointment with this ID
    appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one_or_none()

    # Redirect to appointments page if appointment not found
    if not appointment or appointment.this_user.id != current_user.id:
        flash("You do not have permission to view this appointment", "error")
        return redirect(url_for(f"appointments.{current_user_field}_appointments"))

    # Initialise form to update appointment
    if current_user.role == UserRole.THERAPIST:
        update_appointment_form = TherapistUpdateAppointmentForm(
            id="therapist-update-appointment-form",
            endpoint=url_for(
                "appointment.update_appointment_therapist",
                appointment_id=appointment_id,
            ),
            obj=appointment,
        )
    elif current_user.role == UserRole.CLIENT:
        update_appointment_form = None

    # Render the page with the appointment details and forms
    return render_template(
        "appointment.html",
        appointment=appointment,
        update_appointment_form=update_appointment_form,
    )


@bp.route("/update/<int:appointment_id>/therapist", methods=["POST"])
@therapist_required
@login_required
def update_appointment_therapist(appointment_id):
    # Fetch appointment with this ID
    appointment: Appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Redirect if appointment does not belong to this therapist
    if not appointment or current_user.id != appointment.therapist.user_id:
        flash("You do not have permission to perform this action", "error")
        return redirect(url_for("appointments.therapist_appointments"))

    form = TherapistUpdateAppointmentForm()

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

    # COMPLETED - do nothing
    elif new_status == AppointmentStatus.COMPLETED:
        pass

    # CANCELLED - notify client
    elif new_status == AppointmentStatus.CANCELLED:
        send_appointment_update_email(
            appointment=appointment,
            recipient=appointment.client.user,
            subject=EmailSubject.APPOINTMENT_CANCELLED,
        )

    # NO SHOW - notify client
    elif new_status == AppointmentStatus.NO_SHOW:
        send_appointment_update_email(
            appointment=appointment,
            recipient=appointment.client.user,
            subject=EmailSubject.APPOINTMENT_NO_SHOW_CLIENT,
        )

    else:
        return jsonify(
            {"success": False, "errors": {"action": "Invalid action selected"}}
        )

    # Update the appointment status with form data
    appointment.appointment_status = new_status
    db.session.commit()

    # Redirect to appointment page
    flash("Appointment updated", "success")
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
