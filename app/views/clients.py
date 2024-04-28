from flask import (
    Blueprint,
    Response,
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

from app import db

from app.forms.users import UserProfileForm
from app.forms.clients import ClientProfileForm
from app.models.client import Client
from app.models.enums import UserRole
from app.models.issue import Issue
from app.utils.decorators import client_required, therapist_required
from app.utils.formatters import get_flashed_message_html

bp = Blueprint("clients", __name__, url_prefix="/clients")


@bp.route("/", methods=["GET"])
@login_required
@therapist_required
def index() -> Response:
    # Initialise filter form with fields prepopulated from session
    # filter_form = FilterClientsForm(
    #     id="filter-clients",
    #     endpoint=url_for("clients.filter"),
    #     data=session.get("client_filters", {}),
    # )

    # Fetch all clients which the current therapist has appointments with
    clients = current_user.therapist.clients

    # Render template
    return render_template(
        "clients.html",
        # filter_form=filter_form,
        clients=clients,
    )


@bp.route("/new", methods=["GET"])
@login_required
@client_required
def new_client() -> Response:
    # Redirect user to their profile if it already exists
    if current_user.client:
        return redirect(url_for("clients.client", client_id=current_user.client.id))

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
        default_section="edit-profile",
        forms=forms,
    )


@bp.route("/<int:client_id>", methods=["GET"])
@login_required
def client(client_id: int) -> Response:
    # Get client with this ID
    client: Client = db.session.execute(
        db.select(Client).filter_by(id=client_id)
    ).scalar_one_or_none()

    # Redirect to clients if client not found or not authorised
    if (
        not client
        or (current_user.role == UserRole.CLIENT and not client.is_current_user)
        or (
            current_user.role == UserRole.THERAPIST
            and client.get_appointments_with_therapist(current_user.therapist) is None
        )
    ):
        flash("You do not have permission to view this page", "error")
        return redirect(url_for("clients.index"))

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

    # Render template with information for this therapist
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

    # Redirect to client directory if not authorised
    if not client or not client.is_current_user:
        flash("You do not have permission to perform this action", "error")
        return jsonify(
            {
                "success": False,
                "url": url_for("clients.client", client_id=client_id),
            }
        )

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
