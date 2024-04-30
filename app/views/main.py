from flask import Blueprint, Response, redirect, render_template, url_for
from flask_login import current_user

bp = Blueprint("main", __name__)


@bp.route("/")
@bp.route("/home")
def index() -> Response:
    if current_user.is_authenticated:
        # TODO
        # return render_template("dashboard.html", active_page="home")
        return redirect(url_for("profile.profile", user_id=current_user.id))
    else:
        return render_template("index.html", active_page="home")


@bp.route("/error")
def error() -> Response:
    raise Exception
