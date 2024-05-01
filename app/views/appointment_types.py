from flask import Blueprint, abort, flash, jsonify, url_for
from flask_login import current_user, login_required

from app import db
from app.forms.appointment_types import (AppointmentTypeForm,
                                         DeleteAppointmentTypeForm)
from app.models.appointment_type import AppointmentType
from app.utils.decorators import therapist_required

bp = Blueprint("appointment_types", __name__, url_prefix="/appointment-types")


@bp.route("/create", methods=["POST"])
@login_required
@therapist_required
def create():
    form = AppointmentTypeForm(prefix="new")

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors, "form_prefix": "new"})

    # Create a new appointment type
    new_appointment_type = AppointmentType(
        therapist_id=current_user.therapist.id,
        therapy_type=form.therapy_type.data,
        therapy_mode=form.therapy_mode.data,
        duration=form.duration.data,
        fee_amount=form.fee_amount.data,
        fee_currency=form.fee_currency.data,
        active=True,
    )
    db.session.add(new_appointment_type)
    db.session.commit()

    flash("Appointment type created", "success")
    return jsonify(
        {
            "success": True,
            "url": url_for(
                "therapists.therapist",
                therapist_id=current_user.therapist.id,
                section="appointment-types",
            ),
        }
    )


@bp.route("/update/<int:appointment_type_id>", methods=["POST"])
@login_required
@therapist_required
def update(appointment_type_id):
    # Find the appointment type by ID
    appointment_type = db.get_or_404(AppointmentType, appointment_type_id)

    # Appointment type does not belong to this therapist
    if appointment_type.therapist.user.id != current_user.id:
        abort(403)

    form = AppointmentTypeForm(prefix=str(appointment_type_id))

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify(
            {
                "success": False,
                "errors": form.errors,
                "form_prefix": appointment_type_id,
            }
        )

    # Soft delete - mark existing appointment type as inactive for integrity
    appointment_type.active = False

    # Create a new appointment type
    new_appointment_type = AppointmentType(
        therapist_id=current_user.therapist.id,
        therapy_type=form.therapy_type.data,
        therapy_mode=form.therapy_mode.data,
        duration=form.duration.data,
        fee_amount=form.fee_amount.data,
        fee_currency=form.fee_currency.data,
        active=True,
    )
    db.session.add(new_appointment_type)
    db.session.commit()

    flash("Appointment type updated", "success")
    return jsonify(
        {
            "success": True,
            "url": url_for(
                "therapists.therapist",
                therapist_id=current_user.therapist.id,
                section="appointment-types",
            ),
        }
    )


@bp.route("/delete", methods=["POST"])
@login_required
@therapist_required
def delete():
    # Retrieve appointment type ID from hidden field in form
    form = DeleteAppointmentTypeForm()
    appointment_type_id = form.appointment_type_id.data

    # Fetch appointment with this ID
    appointment_type = db.session.execute(
        db.select(AppointmentType).filter_by(
            id=appointment_type_id, therapist_id=current_user.therapist.id
        )
    ).scalar_one()

    # Appointment type does not belong to this therapist
    if appointment_type.therapist.user.id != current_user.id:
        abort(403)

    # Soft delete appointment to maintain historical integrity
    appointment_type.active = False
    db.session.commit()

    # Redirect to appointment types page
    flash("Appointment type deleted", "warning")
    return jsonify(
        {
            "success": True,
            "url": url_for(
                "therapists.therapist",
                therapist_id=current_user.therapist.id,
                section="appointment-types",
            ),
        }
    )
