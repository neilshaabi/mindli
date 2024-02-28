from flask import Blueprint, flash, jsonify, render_template, request, url_for
from flask_login import current_user, login_required

from app import BlueprintName, db
from app.forms.profile import TherapistForm
from app.models import (
    Issue,
    Language,
    Therapist,
    therapist_format,
    therapist_issue,
    therapist_language,
)

bp = Blueprint(BlueprintName.PROFILE.value, __name__)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    therapist_form = TherapistForm()
    therapist_form.languages.choices = [
        (language.id, language.name)
        for language in db.session.execute(db.select(Language)).scalars()
    ]
    therapist_form.languages.choices = [
        (issue.id, issue.name)
        for issue in db.session.execute(db.select(Issue)).scalars()
    ]

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
        affilitation=form.affiliation.data,
        bio=form.bio.data,
        link=form.link.data,
        location=form.location.data,
        registrations=form.registrations.data,
        qualifications=form.qualifications.data,
        years_of_experience=form.years_of_experience.data,
    )
    db.session.add(therapist)

    # Insert therapist's languages
    therapist_languages = [
        {"therapist_id": therapist.id, "language_id": language_id}
        for language_id in form.languages.data
    ]
    db.session.execute(therapist_language.insert(), therapist_languages)

    # Insert therapist's specialisations
    therapist_issues = [
        {"therapist_id": therapist.id, "issue_id": issue_id}
        for issue_id in form.issues.data
    ]
    db.session.execute(therapist_issue.insert(), therapist_issues)

    # Insert therapist's session formats
    therapist_formats = [
        {"therapist_id": therapist.id, "session_format": session_format}
        for session_format in form.session_formats.data
    ]
    db.session.execute(therapist_format.insert(), therapist_formats)

    db.session.commit()
    flash("Profile information successfully updated!")
    return jsonify(
        {"success": True, "url": url_for(f"{BlueprintName.PROFILE.value}.profile")}
    )
