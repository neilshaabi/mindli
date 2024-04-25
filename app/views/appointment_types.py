from flask import Blueprint, flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.forms.appointment_types import (AppointmentTypeForm,
                                         DeleteAppointmentTypeForm)
from app.models.appointment_type import AppointmentType
from app.utils.decorators import therapist_required

bp = Blueprint("appointment_types", __name__, url_prefix="/appointment-types")


@bp.route("/", methods=["GET"])
@login_required
@therapist_required
def index():
    # Query active appointment types for this therapist
    appointment_types = (
        db.session.execute(
            db.select(AppointmentType).where(
                (AppointmentType.therapist_id == current_user.therapist.id)
                & (AppointmentType.active == True)
            )
        )
        .scalars()
        .all()
    )

    # Create a list of forms pre-populated with the data from each appointment type
    update_forms = [
        AppointmentTypeForm(
            obj=appointment_type,
            prefix=str(appointment_type.id),
            id=f"appointment_type_{appointment_type.id}",
            endpoint=url_for(
                "appointment_types.update",
                appointment_type_id=appointment_type.id,
            ),
        )
        for appointment_type in appointment_types
    ]

    # Add an empty form for adding a new appointment type
    create_form = AppointmentTypeForm(
        prefix="new",
        id="appointment_type_new",
        endpoint=url_for("appointment_types.create"),
    )

    # Add form to delete a given appointment type
    delete_form = DeleteAppointmentTypeForm(
        id="delete_appointment_type",
        endpoint=url_for("appointment_types.delete"),
    )

    # Render the page with the appointment forms
    return render_template(
        "appointment_types.html",
        update_forms=update_forms,
        create_form=create_form,
        delete_form=delete_form,
    )


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

    flash("New appointment type created", "success")
    return jsonify({"success": True, "url": url_for("appointment_types.index")})


@bp.route("/update/<int:appointment_type_id>", methods=["POST"])
@login_required
@therapist_required
def update(appointment_type_id):
    # Find the appointment type by ID
    appointment_type = db.session.execute(
        db.select(AppointmentType).filter_by(
            id=appointment_type_id, therapist_id=current_user.therapist.id
        )
    ).scalar_one_or_none()

    # Redirect if appointment type not found
    if not appointment_type or appointment_type.therapist.user.id != current_user.id:
        return redirect(url_for("appointment_types.index"))

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

    # Mark existing appointment type as inactive to maintain historical integrity
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
    return jsonify({"success": True, "url": url_for("appointment_types.index")})


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

    # Redirect if appointment type does not belong to this therapist
    if appointment_type.therapist.user.id != current_user.id:
        return redirect(url_for("appointment_types.index"))

    # Soft delete appointment to maintain historical integrity
    appointment_type.active = False
    db.session.commit()

    # Redirect to appointment types page
    flash("Appointment type deleted", "success")
    return jsonify({"success": True, "url": url_for("appointment_types.index")})
