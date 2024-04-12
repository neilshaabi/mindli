from flask import Blueprint, jsonify, render_template, render_template_string, url_for
from flask_login import login_required

from app import db
from app.forms.therapists import FilterTherapistsForm
from app.models.appointment_type import AppointmentType
from app.models.enums import TherapyMode, TherapyType
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.therapist import Therapist
from app.models.title import Title

bp = Blueprint("therapist_directory", __name__)


@bp.route("/therapists", methods=["GET"])
@login_required
def therapists():
    filter_form = FilterTherapistsForm(
        id="filter-therapists",
        endpoint=url_for("therapist_directory.filtered_therapists"),
    )

    therapists = db.session.execute(db.select(Therapist)).scalars().all()

    # Render a template, passing the filter form to it
    return render_template(
        "therapist_directory.html", filter_form=filter_form, therapists=therapists
    )


@bp.route("/therapists", methods=["POST"])
@login_required
def filtered_therapists():
    filter_form = FilterTherapistsForm(
        id="filter-therapists",
        endpoint=url_for("therapist_directory.filtered_therapists"),
    )

    # Invalid form submission - return errors
    if not filter_form.validate_on_submit():
        return jsonify({"success": False, "errors": filter_form.errors})

    # Begin building the base query
    query = db.select(Therapist)

    # Apply filters using conditional statements
    if filter_form.therapy_type.data:
        therapy_type = TherapyType[filter_form.therapy_type.data]
        query = query.where(Therapist.appointment_types.any(therapy_type=therapy_type))

    if filter_form.therapy_mode.data:
        modes = [TherapyMode[mode] for mode in filter_form.therapy_mode.data]
        for mode in modes:
            query = query.where(
                Therapist.appointment_types.any(AppointmentType.therapy_mode == mode)
            )

    if filter_form.duration.data:
        query = query.where(
            Therapist.appointment_types.any(duration=filter_form.duration.data)
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

    therapists_html = render_template_string(
        """
        {% from "_macros.html" import therapist_card %}
        {% for therapist in therapists %}
            {{ therapist_card(therapist) }}
        {% endfor %}
    """,
        therapists=filtered_therapists,
    )

    return jsonify(
        {
            "success": True,
            "update_target": "therapist-cards",
            "updated_html": therapists_html,
        }
    )
