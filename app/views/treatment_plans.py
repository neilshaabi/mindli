from datetime import datetime

from flask import Blueprint, abort, jsonify
from flask_login import current_user, login_required

from app import db
from app.forms.treatment_plans import TreatmentPlanForm
from app.models.client import Client
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.therapist import Therapist
from app.models.treatment_plan import TreatmentPlan
from app.utils.decorators import therapist_required
from app.utils.formatters import get_flashed_message_html

bp = Blueprint("treatment_plan", __name__, url_prefix="/treatment-plan")


@bp.route("/create/<int:therapist_id>/<int:client_id>", methods=["POST"])
@login_required
@therapist_required
def create(therapist_id: int, client_id: int):
    # Fetch therapist and client to for this treatment plan
    therapist = db.get_or_404(Therapist, therapist_id)
    client = db.get_or_404(Client, client_id)

    # Prevent unauthorised access
    if therapist_id != current_user.id or client not in therapist.clients:
        abort(403)

    form = TreatmentPlanForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Create a new treatment plan
    plan = TreatmentPlan(
        therapist_id=therapist.id,
        client_id=client.id,
        issues_description=form.issues_description.data,
        interventions_description=form.interventions_description.data,
        goals=form.goals.data,
        medication=form.medication.data,
        last_updated=datetime.now(),
    )
    db.session.add(plan)
    db.session.flush()

    # Update data in association tables
    form.issues.update_association_data(parent=plan, child=Issue, children="issues")
    form.interventions.update_association_data(
        parent=plan, child=Intervention, children="interventions"
    )
    db.session.commit()

    return jsonify(
        {
            "success": True,
            # "url": url_for(
            #     "profile.profile",
            #     user_id=client.user.id,
            #     section="treatment-plan",
            # ),
            "flashed_message_html": get_flashed_message_html(
                "Treatment plan created",
                "success",
            ),
        }
    )


@bp.route("/update/<int:plan_id>", methods=["POST"])
@login_required
@therapist_required
def update(plan_id: int):
    # Find the appointment type by ID
    plan = db.get_or_404(TreatmentPlan, plan_id)

    # Ensure plan belongs to current therapist
    if plan.therapist_id != current_user.therapist.id:
        abort(403)

    form = TreatmentPlanForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update plan with form data
    plan.issues_description = form.issues_description.data
    plan.interventions_description = form.interventions_description.data
    plan.goals = form.goals.data
    plan.medication = form.medication.data
    plan.last_updated = datetime.now()
    db.session.flush()

    # Update data in association tables
    form.issues.update_association_data(parent=plan, child=Issue, children="issues")
    form.interventions.update_association_data(
        parent=plan, child=Intervention, children="interventions"
    )
    db.session.commit()

    return jsonify(
        {
            "success": True,
            # "url": url_for(
            #     "profile.profile",
            #     user_id=client.user.id,
            #     section="treatment-plan",
            # ),
            "flashed_message_html": get_flashed_message_html(
                "Treatment plan updated",
                "success",
            ),
        }
    )
