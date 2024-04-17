from flask import Blueprint, flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.forms.appointments import AppointmentTypeForm, DeleteAppointmentTypeForm
from app.models.appointment_type import AppointmentType
from app.utils.decorators import therapist_required

bp = Blueprint("appointments", __name__)


@bp.route("/appointments", methods=["GET"])
@login_required
@therapist_required
def appointments():
    # Query existing appointment types for the therapist
    appointment_types = (
        db.session.execute(
            db.select(AppointmentType).filter_by(therapist_id=current_user.therapist.id)
        )
        .scalars()
        .all()
    )

    # Create a list of forms pre-populated with the data from each appointment type
    update_appointment_type_forms = [
        AppointmentTypeForm(
            obj=appointment_type,
            prefix=str(appointment_type.id),
            id=f"appointment_type_{appointment_type.id}",
            endpoint=url_for(
                "appointments.update_appointment_type",
                appointment_type_id=appointment_type.id,
            ),
        )
        for appointment_type in appointment_types
    ]

    # Add an empty form for adding a new appointment type
    create_appointment_type_form = AppointmentTypeForm(
        prefix="new",
        id="appointment_type_new",
        endpoint=url_for("appointments.create_appointment_type"),
    )

    # Add form to delete a given appointment type
    delete_appointment_type_form = DeleteAppointmentTypeForm(
        id="delete_appointment_type",
        endpoint=url_for("appointments.delete_appointment_type"),
    )

    # Render the page with the appointment forms and the new appointment form
    return render_template(
        "appointments.html",
        update_appointment_type_forms=update_appointment_type_forms,
        create_appointment_type_form=create_appointment_type_form,
        delete_appointment_type_form=delete_appointment_type_form,
    )


@bp.route("/appointment-types/create", methods=["POST"])
@login_required
@therapist_required
def create_appointment_type():
    form = AppointmentTypeForm(prefix="new")

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors, "form_prefix": "new"})

    # Create a new appointment type instance
    new_appointment_type = AppointmentType(
        therapist_id=current_user.id,
        therapy_type=form.therapy_type.data,
        therapy_mode=form.therapy_mode.data,
        duration=form.duration.data,
        fee_amount=form.fee_amount.data,
        fee_currency=form.fee_currency.data,
    )
    db.session.add(new_appointment_type)
    db.session.commit()

    flash("New appointment type created")
    return jsonify({"success": True, "url": url_for("appointments.appointments")})


@bp.route("/appointment-types/<int:appointment_type_id>", methods=["POST"])
@login_required
@therapist_required
def update_appointment_type(appointment_type_id):
    # Find the appointment type by ID
    appointment_type: AppointmentType = db.session.execute(
        db.select(AppointmentType).filter_by(
            id=appointment_type_id, therapist_id=current_user.therapist.id
        )
    ).scalar_one()

    # Redirect if appointment type not found
    if appointment_type is None:
        return redirect(url_for("appointments.appointments"))

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

    # Update the appointment type with form data
    appointment_type.therapy_type = form.therapy_type.data
    appointment_type.therapy_mode = form.therapy_mode.data
    appointment_type.duration = form.duration.data
    appointment_type.fee_amount = form.fee_amount.data
    appointment_type.fee_currency = form.fee_currency.data
    db.session.commit()

    flash("Appointment type updated")
    return jsonify({"success": True, "url": url_for("appointments.appointments")})


@bp.route("/appointment-types/delete", methods=["POST"])
@login_required
@therapist_required
def delete_appointment_type():
    form = DeleteAppointmentTypeForm()
    appointment_type = db.session.execute(
        db.select(AppointmentType).filter_by(
            id=form.appointment_type_id.data, therapist_id=current_user.therapist.id
        )
    ).scalar_one()
    db.session.delete(appointment_type)
    db.session.commit()
    flash("Appointment type deleted")
    return jsonify({"success": True, "url": url_for("appointments.appointments")})
