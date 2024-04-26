from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   render_template_string, request, session, url_for)
from flask_login import login_required
from sqlalchemy import func

from app import db
from app.forms.appointments import BookAppointmentForm
from app.forms.therapists import FilterTherapistsForm
from app.models.appointment_type import AppointmentType
from app.models.enums import TherapyMode, TherapyType
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.therapist import Therapist
from app.models.title import Title
from app.models.user import User

bp = Blueprint("therapists", __name__, url_prefix="/therapists")


@bp.route("/", methods=["GET"])
@login_required
def index():
    # Initialise filter form with fields prepopulated from session
    filter_form = FilterTherapistsForm(
        id="filter-therapists",
        endpoint=url_for("therapists.filter"),
        data=session.get("therapist_filters", {}),
    )

    therapists = (
        db.session.execute(db.select(Therapist).join(User).where(User.active))
        .scalars()
        .all()
    )

    # Render a template, passing the filter form to it
    return render_template(
        "therapists.html", filter_form=filter_form, therapists=therapists
    )


@bp.route("/<int:therapist_id>", methods=["GET"])
@login_required
def therapist(therapist_id):
    # Get therapist with this ID
    therapist = db.session.execute(
        db.select(Therapist).filter_by(id=therapist_id)
    ).scalar_one_or_none()

    # Redirect to therapist directory if therapist not found
    if not therapist:
        flash("Therapist not found", "error")
        return redirect(url_for("therapists.index"))

    # Initialise form for client to book an appointment with this therapist
    book_appointment_form = BookAppointmentForm(
        obj=therapist,
        id="book_appointment",
        endpoint=url_for(
            "appointments.create",
            therapist_id=therapist_id,
        ),
    )

    # Render template with information for this therapist
    return render_template(
        "therapist.html",
        therapist=therapist,
        book_appointment_form=book_appointment_form,
    )


@bp.route("/filter", methods=["POST"])
@login_required
def filter():
    filter_form = FilterTherapistsForm(
        id="filter-therapists",
        endpoint=url_for("therapists.filter"),
    )

    # Invalid form submission - return errors
    if not filter_form.validate_on_submit():
        return jsonify({"success": False, "errors": filter_form.errors})

    # Handle submissions via different submit buttons separately
    submit_action = request.form["submit"]

    if submit_action == "filter":
        # Store filter settings in the session
        session["therapist_filters"] = {
            "name": filter_form.name.data,
            "therapy_type": filter_form.therapy_type.data,
            "therapy_mode": filter_form.therapy_mode.data,
            "duration": filter_form.duration.data,
            "titles": filter_form.titles.data,
            "years_of_experience": filter_form.years_of_experience.data,
            "gender": filter_form.gender.data,
            "language": filter_form.language.data,
            "country": filter_form.country.data,
            "specialisations": filter_form.specialisations.data,
            "interventions": filter_form.interventions.data,
        }

        # Begin building the base query
        query = db.select(Therapist).join(User).where(User.active)

        # Apply filters by extending the query with conditions for each filter
        if filter_form.name.data:
            search_term = f"%{filter_form.name.data.lower()}%"
            query = query.where(
                func.lower(User.first_name + " " + User.last_name).like(search_term)
            )

        if filter_form.therapy_type.data:
            therapy_type = TherapyType[filter_form.therapy_type.data]
            query = query.where(
                Therapist.appointment_types.any(
                    (AppointmentType.therapy_type == therapy_type)
                    & (AppointmentType.active == True)
                )
            )

        if filter_form.therapy_mode.data:
            modes = [TherapyMode[mode] for mode in filter_form.therapy_mode.data]
            for mode in modes:
                query = query.where(
                    Therapist.appointment_types.any(
                        (AppointmentType.therapy_mode == mode)
                        & (AppointmentType.active == True)
                    )
                )

        if filter_form.duration.data:
            query = query.where(
                Therapist.appointment_types.any(
                    (AppointmentType.duration == filter_form.duration.data)
                    & (AppointmentType.active == True)
                )
            )

        if filter_form.titles.data:
            for title_id in filter_form.titles.data:
                query = query.where(Therapist.titles.any(Title.id == title_id))

        if filter_form.years_of_experience.data:
            query = query.where(
                Therapist.years_of_experience >= filter_form.years_of_experience.data
            )

        if filter_form.gender.data:
            query = query.where(Therapist.user.has(gender=filter_form.gender.data))

        if filter_form.language.data:
            query = query.where(
                Therapist.languages.any(Language.id == filter_form.language.data)
            )

        if filter_form.country.data:
            query = query.where(Therapist.country == filter_form.country.data)

        if filter_form.specialisations.data:
            for specialisation_id in filter_form.specialisations.data:
                query = query.where(
                    Therapist.specialisations.any(Issue.id == specialisation_id)
                )

        if filter_form.interventions.data:
            for intervention_id in filter_form.interventions.data:
                query = query.where(
                    Therapist.interventions.any(Intervention.id == intervention_id)
                )

        # Execute query to filter therapists
        filtered_therapists = db.session.execute(query).scalars().all()

        # Construct template strings to insert updated therapists via AJAX
        therapists_html = render_template_string(
            """
            {% from "_macros.html" import therapist_card %}
            {% for therapist in therapists %}
                {{ therapist_card(therapist) }}
            {% endfor %}
        """,
            therapists=filtered_therapists,
        )

        filter_count_html = render_template_string(
            "{{ therapists|length }} therapists found",
            therapists=filtered_therapists,
        )

        return jsonify(
            {
                "success": True,
                "update_targets": {
                    "therapist-cards": therapists_html,
                    "filter-count": filter_count_html,
                },
            }
        )

    elif submit_action == "reset_filters":
        # Clear filter settings from the session if they exist
        session.pop("therapist_filters", None)
        return jsonify({"success": True, "url": url_for("therapists.index")})
