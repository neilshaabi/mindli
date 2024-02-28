from flask import Blueprint, flash, jsonify, render_template, request, url_for
from flask_login import current_user, login_required

from app import BlueprintName, db
from app.forms.profile import TherapistProfileForm
from app.models import therapist_format, therapist_issue, therapist_language
from app.models.issue import Issue
from app.models.language import Language
from app.models.session_format import SessionFormatModel
from app.models.therapist import Therapist

bp = Blueprint(BlueprintName.PROFILE.value, __name__)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    therapist_form = TherapistProfileForm()
    therapist_form.languages.choices = [
        (language.id, language.name)
        for language in db.session.execute(db.select(Language)).scalars()
    ]
    therapist_form.issues.choices = [
        (issue.id, issue.name)
        for issue in db.session.execute(db.select(Issue)).scalars()
    ]
    therapist_form.session_formats.choices = [
        (session_format.id, session_format.name)
        for session_format in db.session.execute(
            db.select(SessionFormatModel)
        ).scalars()
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
        {"therapist_id": therapist.id, "session_format_id": session_format_id}
        for session_format_id in form.session_formats.data
    ]
    db.session.execute(therapist_format.insert(), therapist_formats)

    db.session.commit()
    flash("Profile information successfully updated!")
    return jsonify(
        {"success": True, "url": url_for(f"{BlueprintName.PROFILE.value}.profile")}
    )
