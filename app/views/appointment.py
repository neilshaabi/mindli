from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.models.appointment import Appointment
from app.models.appointment_type import AppointmentType
from app.models.enums import AppointmentStatus, EmailSubject, PaymentStatus, UserRole
from app.models.therapist import Therapist
from app.utils.decorators import client_required, therapist_required
from app.utils.mail import EmailMessage
from app.views.stripe import create_checkout_session

bp = Blueprint("appointment", __name__, url_prefix="/appointment")


@bp.route("/<int:appointment_id>", methods=["GET"])
@login_required
def view_appointment(appointment_id):
    # Determine fields to access other user based on the current user's role
    if current_user.role == UserRole.THERAPIST:
        current_user_field = "therapist"  # TODO: REMOVE THIS VARIABLE AND REDIRECT LOGIC ONCE MERGED APPOINTMENTS ROUTE
        other_user_field = "client"
    elif current_user.role == UserRole.CLIENT:
        current_user_field = "client"
        other_user_field = "therapist"

    # Fetch appointment with this ID
    appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one_or_none()

    # Redirect to appointments page if appointment not found
    if (
        not appointment
        or getattr(appointment, current_user_field).user.id != current_user.id
    ):
        return redirect(url_for(f"appointments.{current_user_field}_appointments"))

    appointment.other_user = getattr(appointment, other_user_field).user

    # Render the page with the appointment details and forms
    return render_template("appointment.html", appointment=appointment)


@bp.route("/confirm/<int:appointment_id>", methods=["POST"])
@therapist_required
@login_required
def confirm_appointment(appointment_id):
    # Fetch appointment with this ID
    appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one

    # Redirect if appointment does not belong to this therapist
    if current_user.id != appointment.therapist.user_id:
        return redirect(url_for("appointments.therapist_appointments"))

    # Set status of appointment to CONFIRMED
    appointment.appointment_status = AppointmentStatus.CONFIRMED
    db.session.commit()

    # Send email to client
    email = EmailMessage(
        recipient=appointment.client.user,
        subject=EmailSubject.APPOINTMENT_CONFIRMED_CLIENT,
        context={
            "therapist_name": f"{appointment.therapist.user.first_name} {appointment.therapist.user.last_name}",
            "appointment_date": appointment.time.strftime("%d %B %Y"),
            "appointment_time": appointment.time.strftime("%I:%M %p"),
        },
        url_params={"appointment_id": appointment.id},
    )
    email.send()

    # Redirect to appointments page
    flash("Appointment confirmed", "success")
    return jsonify(
        {
            "success": True,
            "url": url_for(
                "appointment.view_appointment", appointment_id=appointment.id
            ),
        }
    )
