import os

from flask import (
    Blueprint,
    Response,
    current_app,
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
from sqlalchemy import func
from werkzeug.utils import secure_filename

from app import db
from app.forms.appointments import BookAppointmentForm
from app.forms.profile import TherapistProfileForm, UserProfileForm
from app.forms.therapists import FilterTherapistsForm
from app.models.appointment_type import AppointmentType
from app.models.enums import TherapyMode, TherapyType, UserRole
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.therapist import Therapist
from app.models.title import Title
from app.models.user import User
from app.utils.files import get_file_extension
from app.utils.formatters import get_flashed_message_html

bp = Blueprint("therapists", __name__, url_prefix="/therapists")


@bp.route("/", methods=["GET"])
@login_required
def index() -> Response:
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
def therapist(therapist_id: int) -> Response:
    # Get therapist with this ID
    therapist = db.session.execute(
        db.select(Therapist).filter_by(id=therapist_id)
    ).scalar_one_or_none()

    # Redirect to therapist directory if therapist not found
    if not therapist:
        flash("Therapist not found", "error")
        return redirect(url_for("therapists.index"))

    user_profile_form = None
    therapist_profile_form = None
    book_appointment_form = None

    # Initialise forms for current user to edit their profile
    if therapist.user.id == current_user.id:
        user_profile_form = UserProfileForm(
            obj=current_user,
            id="user-profile",
            endpoint=url_for("profile.user_profile"),
        )

        therapist_profile_form = TherapistProfileForm(
            obj=current_user.therapist,
            id="therapist-profile",
            endpoint=url_for("therapists.update", therapist_id=therapist_id),
        )

    # Initialise form for client to book an appointment with this therapist
    elif current_user.role == UserRole.CLIENT:
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
        user_profile_form=user_profile_form,
        therapist_profile_form=therapist_profile_form,
        book_appointment_form=book_appointment_form,
    )


@bp.route("/<int:therapist_id>/update", methods=["POST"])
@login_required
def update(therapist_id: int) -> Response:
    # Initialise submitted form
    form = TherapistProfileForm()

    # Get therapist with this ID
    therapist = db.session.execute(
        db.select(Therapist).filter_by(id=therapist_id)
    ).scalar_one_or_none()

    # Redirect to therapist directory if therapist not found
    if not therapist or therapist.user.id != current_user.id:
        flash("You do not have permission to perform this action", "error")
        return jsonify(
            {
                "success": False,
                "url": url_for("therapists.therapist", therapist_id=therapist_id),
            }
        )

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update Therapist with form data
    therapist.country = form.country.data
    therapist.link = form.link.data
    therapist.location = form.location.data
    therapist.years_of_experience = form.years_of_experience.data
    therapist.qualifications = form.qualifications.data
    therapist.registrations = form.registrations.data
    form.titles.update_association_data(
        parent=therapist, child=Title, children="titles"
    )
    form.languages.update_association_data(
        parent=therapist, child=Language, children="languages"
    )
    form.issues.update_association_data(
        parent=therapist, child=Issue, children="specialisations"
    )
    form.interventions.update_association_data(
        parent=therapist, child=Intervention, children="interventions"
    )

    db.session.commit()

    # Flash message using AJAX
    return jsonify(
        {
            "success": True,
            "flashed_message_html": get_flashed_message_html(
                "Profile updated successfully", "success"
            ),
        }
    )


@bp.route("/filter", methods=["POST"])
@login_required
def filter() -> Response:
    # Initialise submitted form
    form = FilterTherapistsForm(
        id="filter-therapists",
        endpoint=url_for("therapists.filter"),
    )

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Handle submissions via different submit buttons separately
    submit_action = request.form["submit"]

    if submit_action == "filter":
        # Store filter settings in the session
        session["therapist_filters"] = {
            "name": form.name.data,
            "therapy_type": form.therapy_type.data,
            "therapy_mode": form.therapy_mode.data,
            "duration": form.duration.data,
            "titles": form.titles.data,
            "years_of_experience": form.years_of_experience.data,
            "gender": form.gender.data,
            "language": form.language.data,
            "country": form.country.data,
            "specialisations": form.specialisations.data,
            "interventions": form.interventions.data,
        }

        # Begin building the base query
        query = db.select(Therapist).join(User).where(User.active)

        # Apply filters by extending the query with conditions for each filter
        if form.name.data:
            search_term = f"%{form.name.data.lower()}%"
            query = query.where(
                func.lower(User.first_name + " " + User.last_name).like(search_term)
            )

        if form.therapy_type.data:
            therapy_type = TherapyType[form.therapy_type.data]
            query = query.where(
                Therapist.appointment_types.any(
                    (AppointmentType.therapy_type == therapy_type)
                    & (AppointmentType.active == True)
                )
            )

        if form.therapy_mode.data:
            modes = [TherapyMode[mode] for mode in form.therapy_mode.data]
            for mode in modes:
                query = query.where(
                    Therapist.appointment_types.any(
                        (AppointmentType.therapy_mode == mode)
                        & (AppointmentType.active == True)
                    )
                )

        if form.duration.data:
            query = query.where(
                Therapist.appointment_types.any(
                    (AppointmentType.duration == form.duration.data)
                    & (AppointmentType.active == True)
                )
            )

        if form.titles.data:
            for title_id in form.titles.data:
                query = query.where(Therapist.titles.any(Title.id == title_id))

        if form.years_of_experience.data:
            query = query.where(
                Therapist.years_of_experience >= form.years_of_experience.data
            )

        if form.gender.data:
            query = query.where(Therapist.user.has(gender=form.gender.data))

        if form.language.data:
            query = query.where(
                Therapist.languages.any(Language.id == form.language.data)
            )

        if form.country.data:
            query = query.where(Therapist.country == form.country.data)

        if form.specialisations.data:
            for specialisation_id in form.specialisations.data:
                query = query.where(
                    Therapist.specialisations.any(Issue.id == specialisation_id)
                )

        if form.interventions.data:
            for intervention_id in form.interventions.data:
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
