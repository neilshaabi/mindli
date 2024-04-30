from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    jsonify,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import func

from app import db
from app.forms.appointment_types import AppointmentTypeForm, DeleteAppointmentTypeForm
from app.forms.appointments import BookAppointmentForm
from app.forms.stripe import CreateStripeAccountForm
from app.forms.therapists import FilterTherapistsForm, TherapistProfileForm
from app.forms.users import UserProfileForm
from app.models.appointment_type import AppointmentType
from app.models.enums import TherapyMode, TherapyType, UserRole
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.therapist import Therapist
from app.models.title import Title
from app.models.user import User
from app.utils.decorators import therapist_required

bp = Blueprint("therapists", __name__, url_prefix="/therapists")
FILTERS_SESSION_KEY = "therapist_filters"


@bp.route("/", methods=["GET"])
def index() -> Response:
    # Initialise filter form with fields prepopulated from session
    filter_form = FilterTherapistsForm(
        id="filter-therapists",
        endpoint=url_for("therapists.filter"),
        data=session.get(FILTERS_SESSION_KEY, {}),
    )

    # Fetch all active therapists
    therapists = (
        db.session.execute(
            db.select(Therapist)
            .join(User)
            .where(User.active)
            .where(Therapist.appointment_types.any(AppointmentType.active == True))
        )
        .scalars()
        .all()
    )

    # Render template
    return render_template(
        "therapists.html",
        active_page="therapists",
        filter_form=filter_form,
        therapists=therapists,
    )


@bp.route("/new", methods=["GET"])
@login_required
@therapist_required
def new_therapist() -> Response:
    # Current user's therapist profile already exists
    if current_user.onboarding_complete:
        abort(403)

    # Create mock Therapist to pass to template
    mock_therapist = Therapist(user=current_user)

    # Initialise dictionary to hold all forms
    forms = {
        "user_profile_form": UserProfileForm(
            obj=current_user,
            id="user-profile",
            endpoint=url_for("user.update", user_id=current_user.id),
        ),
        "therapist_profile_form": TherapistProfileForm(
            id="therapist-profile",
            endpoint=url_for("therapists.create"),
        ),
        "create_appt_type_form": AppointmentTypeForm(
            prefix="new",
            id="appointment_type_new",
            endpoint=url_for("appointment_types.create"),
        ),
        "stripe_onboarding_form": CreateStripeAccountForm(
            id="stripe-onboarding-form",
            endpoint=url_for("stripe.create_account"),
        ),
    }

    # Render template with information for this therapist
    return render_template(
        "therapist.html",
        active_page="profile",
        therapist=mock_therapist,
        default_section="profile",
        forms=forms,
    )


@bp.route("/<int:therapist_id>", methods=["GET"])
@login_required
def therapist(therapist_id: int) -> Response:
    # Fetch therapist with this ID
    therapist = db.get_or_404(Therapist, therapist_id)

    # Initialise dictionary to hold all forms
    forms = {
        "user_profile_form": None,
        "therapist_profile_form": None,
        "create_appt_type_form": None,
        "delete_appt_type_form": None,
        "update_appt_type_forms": [],
        "book_appointment_form": None,
        "stripe_onboarding_form": None,
    }

    if therapist.is_current_user:
        active_page = "profile"

        # Initialise forms for current user to edit their profile
        forms["user_profile_form"] = UserProfileForm(
            obj=current_user,
            id="user-profile",
            endpoint=url_for("user.update", user_id=current_user.id),
        )

        forms["therapist_profile_form"] = TherapistProfileForm(
            obj=current_user.therapist,
            id="therapist-profile",
            endpoint=url_for("therapists.update", therapist_id=therapist_id),
        )

        forms["create_appt_type_form"] = AppointmentTypeForm(
            prefix="new",
            id="appointment_type_new",
            endpoint=url_for("appointment_types.create"),
        )

        forms["delete_appt_type_form"] = DeleteAppointmentTypeForm(
            id="delete_appointment_type",
            endpoint=url_for("appointment_types.delete"),
        )

        forms["update_appt_type_forms"] = [
            AppointmentTypeForm(
                obj=appointment_type,
                prefix=str(appointment_type.id),
                id=f"appointment_type_{appointment_type.id}",
                endpoint=url_for(
                    "appointment_types.update",
                    appointment_type_id=appointment_type.id,
                ),
            )
            for appointment_type in therapist.active_appointment_types
        ]

        forms["stripe_onboarding_form"] = CreateStripeAccountForm(
            id="stripe-onboarding-form",
            endpoint=url_for("stripe.create_account"),
        )

    # Not current user
    else:
        active_page = "therapists"

        if current_user.role == UserRole.CLIENT:
            forms["book_appointment_form"] = BookAppointmentForm(
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
        active_page=active_page,
        therapist=therapist,
        default_section=request.args.get("section", "profile"),
        TherapyType=TherapyType,
        TherapyMode=TherapyMode,
        forms=forms,
    )


@bp.route("/create", methods=["POST"])
@login_required
@therapist_required
def create() -> Response:
    # Initialise submitted form
    form = TherapistProfileForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Create Therapist with form data
    therapist = Therapist(
        user_id=current_user.id,
        years_of_experience=form.years_of_experience.data,
        qualifications=form.qualifications.data,
        registrations=form.registrations.data,
        country=form.country.data,
        location=form.location.data,
        link=form.link.data,
    )
    db.session.add(therapist)
    db.session.flush()

    # Update data in association tables
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

    # Flash message via AJAX
    flash("Therapist profile created", "success")
    return jsonify(
        {
            "success": True,
            "url": url_for(
                "profile.profile", user_id=current_user.id, section="edit-profile"
            ),
        }
    )


@bp.route("/<int:therapist_id>/update", methods=["POST"])
@login_required
@therapist_required
def update(therapist_id: int) -> Response:
    # Get therapist with this ID
    therapist = db.get_or_404(Therapist, therapist_id)

    # Current user is not authorised
    if not therapist.is_current_user:
        abort(403)

    # Initialise submitted form
    form = TherapistProfileForm()

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

    # Update data in association tables
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

    # Flash message and reload page to propagate changes
    flash("Therapist profile updated", "success")
    return jsonify(
        {
            "success": True,
            "url": url_for(
                "profile.profile", user_id=current_user.id, section="edit-profile"
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
        form.store_data_in_session(FILTERS_SESSION_KEY)

        # Build base query for active therapists with active appointment types
        query = (
            db.select(Therapist)
            .join(User)
            .where(User.active)
            .where(Therapist.appointment_types.any(AppointmentType.active == True))
        )

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
            {% from "_macros.html" import therapist_cards with context %}
            {{ therapist_cards(therapists) }}
        """,
            therapists=filtered_therapists,
        )

        filter_count_html = render_template_string(
            "{{ therapists|length if therapists else 0}} therapists found",
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

    # Clear filter settings from the session if they exist
    elif submit_action == "reset_filters":
        session.pop(FILTERS_SESSION_KEY, None)
        return jsonify({"success": True, "url": url_for("therapists.index")})
