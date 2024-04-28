from flask import Blueprint, Response, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.models.enums import UserRole

bp = Blueprint("main", __name__)


@bp.route("/")
@bp.route("/index")
def index() -> Response:
    return render_template("index.html")


@bp.route("/profile", methods=["GET"])
@login_required
def profile():
    if current_user.role == UserRole.THERAPIST:
        if current_user.therapist:
            return redirect(
                url_for("therapists.therapist", therapist_id=current_user.therapist.id)
            )
        else:
            return redirect(url_for("therapists.new_therapist"))

    elif current_user.role == UserRole.CLIENT:
        if current_user.client:
            return redirect(url_for("clients.client", client_id=current_user.client.id))
        else:
            return redirect(url_for("clients.new_client"))

    else:
        print("Unhandled user role")
        return redirect(url_for("main.index"))


@bp.route("/error")
def error() -> Response:
    raise Exception
