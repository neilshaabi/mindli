from flask import Blueprint, Response, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
@bp.route("/index")
def index() -> Response:
    return render_template("index.html", active_page="home")


@bp.route("/error")
def error() -> Response:
    raise Exception
