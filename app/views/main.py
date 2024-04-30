from flask import Blueprint, Response, render_template
from flask_login import current_user

bp = Blueprint("main", __name__)


@bp.route("/")
@bp.route("/home")
def index() -> Response:
    if current_user.is_authenticated:
        return render_template("dashboard.html", active_page="home")
    else:
        return render_template("index.html", active_page="home")


@bp.route("/error")
def error() -> Response:
    raise Exception
