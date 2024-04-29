from datetime import timedelta

from flask import (Blueprint, Response, abort, jsonify, redirect,
                   render_template, render_template_string, request, session,
                   url_for)
from flask_login import current_user, login_required
from sqlalchemy import func

from app import db
from app.forms.clients import ClientProfileForm, FilterClientsForm
from app.forms.users import UserProfileForm
from app.models.appointment import Appointment
from app.models.client import Client
from app.models.enums import UserRole
from app.models.issue import Issue
from app.models.user import User
from app.utils.decorators import client_required, therapist_required
from app.utils.formatters import age_to_date_of_birth, get_flashed_message_html

bp = Blueprint("clients", __name__, url_prefix="/clients")
FILTERS_SESSION_KEY = "client_filters"


@bp.route("/", methods=["GET"])
@login_required
@therapist_required
def index() -> Response:
    # Initialise filter form with fields prepopulated from session
    filter_form = FilterClientsForm(
        id="filter-clients",
        endpoint=url_for("clients.filter"),
        data=session.get(FILTERS_SESSION_KEY, {}),
    )

    if current_user.therapist:
        # Retrieve client IDs through appointments with the current therapist
        client_ids_query = (
            db.select(Appointment.client_id)
            .where(Appointment.therapist_id == current_user.therapist.id)
            .distinct()
        ).subquery()

        # Fetch clients the therapist has seen
        clients = (
            db.session.execute(
                db.select(Client).where(
                    Client.id.in_(db.select(client_ids_query.c.client_id))
                )
            )
            .scalars()
            .all()
        )

    else:
        clients = None

    # Render template
    return render_template(
        "clients.html",
        filter_form=filter_form,
        clients=clients,
    )


@bp.route("/new", methods=["GET"])
@login_required
@client_required
def new_client() -> Response:
    # Redirect user to their profile if it already exists
    if current_user.client:
        return redirect(
            url_for(
                "profile.profile",
                role=current_user.role.value,
                role_specific_id=current_user.role_specific_id,
            )
        )

    # Create mock Client to pass to template
    mock_client = Client(user=current_user)

    # Initialise dictionary to hold all forms
    forms = {
        "user_profile_form": UserProfileForm(
            obj=current_user,
            id="user-profile",
            endpoint=url_for("user.update", user_id=current_user.id),
        ),
        "client_profile_form": ClientProfileForm(
            id="client-profile",
            endpoint=url_for("clients.create"),
        ),
    }

    # Render template with information for this client
    return render_template(
        "client.html",
        client=mock_client,
        default_section="profile",
        forms=forms,
    )


@bp.route("/<int:client_id>", methods=["GET"])
@login_required
def client(client_id: int) -> Response:
    # Get client with this ID
    client: Client = db.session.execute(
        db.select(Client).filter_by(id=client_id)
    ).scalar_one_or_none()

    # Client not found
    if not client:
        abort(400)

    # Current user is a client who is not the current user
    if current_user.role == UserRole.CLIENT and not client.is_current_user:
        abort(403)

    # Current user is a therapist with no appointments with this client
    elif (
        current_user.role == UserRole.THERAPIST
        and client.get_appointments_with_therapist(current_user.therapist) is None
    ):
        abort(403)

    # Initialise dictionary to hold all forms
    forms = {
        "user_profile_form": None,
        "client_profile_form": None,
    }

    # Initialise forms for current user to edit their profile
    if client.is_current_user:
        forms["user_profile_form"] = UserProfileForm(
            obj=current_user,
            id="user-profile",
            endpoint=url_for("user.update", user_id=current_user.id),
        )

        forms["client_profile_form"] = ClientProfileForm(
            obj=current_user.client,
            id="client-profile",
            endpoint=url_for("clients.update", client_id=client_id),
        )

    # Render template with information for this client
    return render_template(
        "client.html",
        client=client,
        default_section=request.args.get("section", "profile"),
        forms=forms,
    )


@bp.route("/create", methods=["POST"])
@login_required
@client_required
def create() -> Response:
    # Initialise submitted form
    form = ClientProfileForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update Client with form data
    client = Client(
        user_id=current_user.id,
        date_of_birth=form.date_of_birth.data,
        occupation=form.occupation.data,
        address=form.address.data,
        phone=form.phone.data,
        emergency_contact_name=form.emergency_contact_name.data,
        emergency_contact_phone=form.emergency_contact_phone.data,
        referral_source=form.referral_source.data,
    )
    db.session.add(client)
    db.session.flush()

    # Update data in association tables
    form.issues.update_association_data(parent=client, child=Issue, children="issues")
    db.session.commit()

    # Redirect to client profile
    return jsonify(
        {
            "success": True,
            "flashed_message": get_flashed_message_html(
                "Client profile created", "success"
            ),
        }
    )


@bp.route("/<int:client_id>/update", methods=["POST"])
@login_required
@client_required
def update(client_id: int) -> Response:
    # Get client with this ID
    client = db.session.execute(
        db.select(Client).filter_by(id=client_id)
    ).scalar_one_or_none()

    # Client not found
    if not client:
        abort(400)

    # Current user is not authorised
    if not client.is_current_user:
        abort(403)

    # Initialise submitted form
    form = ClientProfileForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update Client with form data
    client.date_of_birth = form.date_of_birth.data
    client.occupation = form.occupation.data
    client.address = form.address.data
    client.phone = form.phone.data
    client.emergency_contact_name = form.emergency_contact_name.data
    client.emergency_contact_phone = form.emergency_contact_phone.data
    client.referral_source = form.referral_source.data

    # Update data in association tables
    form.issues.update_association_data(parent=client, child=Issue, children="issues")
    db.session.commit()

    # Flash message via AJAX
    return jsonify(
        {
            "success": True,
            "flashed_message": get_flashed_message_html(
                "Client profile updated", "success"
            ),
        }
    )


@bp.route("/filter", methods=["POST"])
@login_required
@therapist_required
def filter() -> Response:
    # Initialise submitted form
    form = FilterClientsForm(
        id="filter-clients",
        endpoint=url_for("clients.filter"),
    )

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Handle submissions via different submit buttons separately
    submit_action = request.form["submit"]

    if submit_action == "filter":
        # Store filter settings in the session
        form.store_data_in_session(FILTERS_SESSION_KEY)

        # Retrieve client IDs through appointments with the current therapist
        client_ids_query = (
            db.select(Appointment.client_id)
            .where(Appointment.therapist_id == current_user.therapist.id)
            .distinct()
        ).subquery()

        # Begin building the base query, including only clients the therapist has seen
        query = db.select(Client).where(
            Client.id.in_(db.select(client_ids_query.c.client_id))
        )

        # Apply filters by extending the query with conditions for each filter
        if form.name.data:
            search_term = f"%{form.name.data.lower()}%"
            query = query.join(User).where(
                func.lower(User.first_name + " " + User.last_name).like(search_term)
            )

        if form.gender.data:
            query = query.where(Client.user.has(gender=form.gender.data))

        if form.min_age.data:
            min_age_dob = age_to_date_of_birth(form.min_age.data + 1) - timedelta(
                days=1
            )
            query = query.filter(Client.date_of_birth <= min_age_dob)

        if form.max_age.data:
            max_age_dob = age_to_date_of_birth(form.max_age.data)
            query = query.filter(Client.date_of_birth >= max_age_dob)

        if form.occupation.data:
            query = query.where(Client.occupation == form.occupation.data)

        if form.issues.data:
            for issue_id in form.issues.data:
                query = query.where(Client.issues.any(Issue.id == issue_id))

        if form.referral_source.data:
            query = query.where(Client.referral_source == form.referral_source.data)

        # Execute query to filter clients
        filtered_clients = db.session.execute(query).scalars().all()

        # Construct template strings to insert updated clients via AJAX
        clients_html = render_template_string(
            """
            {% from "_macros.html" import client_cards with context %}
            {{ client_cards(clients) }}
        """,
            clients=filtered_clients,
        )

        filter_count_html = render_template_string(
            "{{ clients|length }} clients found",
            clients=filtered_clients,
        )

        return jsonify(
            {
                "success": True,
                "update_targets": {
                    "client-cards": clients_html,
                    "filter-count": filter_count_html,
                },
            }
        )

    # Clear filter settings from the session if they exist
    elif submit_action == "reset_filters":
        session.pop(FILTERS_SESSION_KEY, None)
        return jsonify({"success": True, "url": url_for("clients.index")})
