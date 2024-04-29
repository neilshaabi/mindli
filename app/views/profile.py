from flask import Blueprint, Response, abort, redirect, request, url_for
from flask_login import current_user, login_required

from app.models.enums import UserRole

bp = Blueprint("profile", __name__, url_prefix="/profile")


@bp.route("/", methods=["GET"])
@login_required
def index() -> Response:
    default_section = request.args.get("section")

    if current_user.role == UserRole.THERAPIST:
        if current_user.therapist:
            url = url_for(
                "therapists.therapist",
                therapist_id=current_user.therapist.id,
                section=default_section,
            )
        else:
            url = url_for("therapists.new_therapist", section=default_section)

    elif current_user.role == UserRole.CLIENT:
        if current_user.client:
            url = url_for(
                "clients.client",
                client_id=current_user.client.id,
                section=default_section,
            )
        else:
            url = url_for("clients.new_client")

    else:
        print(f"Unhandled user role: {current_user.role}")
        url = url_for("main.index")

    return redirect(url)


@bp.route("/<role>/<int:role_specific_id>", methods=["GET"])
@login_required
def profile(role: str, role_specific_id: int) -> Response:
    # Validate role from url
    try:
        role = UserRole(role)
    except ValueError:
        abort(404, f"The specified role is invalid: {role}")

    default_section = request.args.get("section")

    # Redirect user to their role-specific profile page
    if role == UserRole.THERAPIST:
        url = url_for(
            "therapists.therapist",
            therapist_id=role_specific_id,
            section=default_section,
        )

    elif role == UserRole.CLIENT:
        url = url_for(
            "clients.client", client_id=role_specific_id, section=default_section
        )

    return redirect(url)
