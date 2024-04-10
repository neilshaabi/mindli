from flask import Blueprint, jsonify, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.therapists import FilterTherapistsForm

from app import db
from app.models.therapist import Therapist

bp = Blueprint("therapists", __name__)


@bp.route("/therapists", methods=["GET"])
@login_required
def therapists():
    filter_form = FilterTherapistsForm(
        id="filter-therapists", endpoint=url_for("therapists.filtered_therapists")
    )

    therapists = db.session.execute(db.select(Therapist)).scalars()

    # Render a template, passing the filter form to it
    return render_template("therapists.html", filter_form=filter_form, therapists=therapists)


@bp.route("/therapists", methods=["POST"])
@login_required
def filtered_therapists():
    filter_form = FilterTherapistsForm(
        id="filter-therapists", endpoint=url_for("therapists.filtered_therapists")
    )

    # Invalid form submission - return errors
    if not filter_form.validate_on_submit():
        return jsonify({"success": False, "errors": filter_form.errors})

    return jsonify({"success": True, "url": url_for("therapists.therapists")})
