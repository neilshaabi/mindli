from flask import Blueprint, render_template, url_for
from flask_login import current_user, login_required
from app import db
from app.forms.availability import AvailabilityForm
from app.models import Availability
from app.utils.decorators import therapist_required

bp = Blueprint("availability", __name__)

@bp.route("/availability", methods=["GET"])
@login_required
@therapist_required
def availability():
    
    # Query existing availabilities for the therapist
    availabilities = (
        db.session.execute(
            db.select(Availability).filter_by(therapist_id=current_user.therapist.id).order_by(Availability.day_of_week)
        )
        .scalars()
        .all()
    )

    # TODO

    return render_template(
        "availability.html",        
    )


