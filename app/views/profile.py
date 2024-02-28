from flask import Blueprint, flash, jsonify, render_template, request, url_for
from flask_login import current_user, login_required

from app import BlueprintName, db
from app.forms.profile import TherapistProfileForm
from app.models import therapist_format, therapist_issue, therapist_language
from app.models.therapist import Therapist

bp = Blueprint(BlueprintName.PROFILE.value, __name__)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    therapist_form = TherapistProfileForm()

    form = therapist_form

    # GET request - display page
    if request.method == "GET":
        return render_template("profile.html", form=form)

    # POST request - validate form
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Insert therapist's profile information
    therapist = Therapist(
        user_id=current_user.id,
        gender=form.gender.data,
        country=form.country.data,
        affiliation=form.affiliation.data,
        bio=form.bio.data,
        link=form.link.data,
        location=form.location.data,
        registrations=form.registrations.data,
        qualifications=form.qualifications.data,
        years_of_experience=form.years_of_experience.data,
    )
    db.session.add(therapist)
    db.session.commit()

    # Insert therapist's languages
    therapist_languages = form.languages.get_association_data(
        parent_id=therapist.id, parent_key="therapist_id", child_key="language_id"
    )
    db.session.execute(therapist_language.insert(), therapist_languages)

    # Insert therapist's specialisations
    therapist_issues = form.issues.get_association_data(
        parent_id=therapist.id, parent_key="therapist_id", child_key="issue_id"
    )
    db.session.execute(therapist_issue.insert(), therapist_issues)

    # Insert therapist's session formats
    therapist_formats = form.session_formats.get_association_data(
        parent_id=therapist.id, parent_key="therapist_id", child_key="session_format_id"
    )
    db.session.execute(therapist_format.insert(), therapist_formats)

    db.session.commit()
    flash("Profile information successfully updated!")
    return jsonify(
        {"success": True, "url": url_for(f"{BlueprintName.PROFILE.value}.profile")}
    )
