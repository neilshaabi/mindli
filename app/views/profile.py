from flask import Blueprint, Response, redirect, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.enums import UserRole
from app.models.user import User

bp = Blueprint("profile", __name__, url_prefix="/profile")


@bp.route("/", methods=["GET"])
@login_required
def index() -> Response:
    default_section = request.args.get("section")
    return redirect(
        url_for("profile.profile", user_id=current_user.id, section=default_section)
    )


@bp.route("/<int:user_id>", methods=["GET"])
@login_required
def profile(user_id: int) -> Response:
    # Fetch user with this id
    user = db.get_or_404(User, user_id)

    default_section = request.args.get("section")

    # Redirect user to their role-specific profile page
    if user.role == UserRole.THERAPIST:
        if user.therapist:
            url = url_for(
                "therapists.therapist",
                therapist_id=user.therapist.id,
                section=default_section,
            )
        else:
            url = url_for("therapists.new_therapist", section=default_section)

    elif user.role == UserRole.CLIENT:
        if user.client:
            url = url_for(
                "clients.client",
                client_id=user.client.id,
                section=default_section,
            )
        else:
            url = url_for("clients.new_client", section=default_section)

    else:
        print(f"Unhandled user role: {current_user.role}")
        url = url_for("main.index")

    return redirect(url)
