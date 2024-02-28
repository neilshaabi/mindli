from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import BlueprintName, db
from app.forms.profile import ClientProfileForm, TherapistProfileForm
from app.models import (
    client_format,
    client_issue,
    therapist_format,
    therapist_issue,
    therapist_language,
)
from app.models.client import Client
from app.models.enums import UserRole
from app.models.therapist import Therapist
from app.utils.decorators import client_required, therapist_required

bp = Blueprint(BlueprintName.PROFILE.value, __name__)


@bp.route("/therapist/profile", methods=["GET", "POST"])
@login_required
@therapist_required
def therapist_profile():
    # Redirect to client page if current user is not a therapist
    if current_user.role != UserRole.THERAPIST:
        flash("You are not authorised to view this page.")
        return redirect(url_for(f"{BlueprintName.PROFILE.value}.client_profile"))

    form = TherapistProfileForm()

    # GET request - display page
    if request.method == "GET":
        return render_template("therapist_profile.html", form=form)

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

    # Successful update - reload page
    flash("Profile information successfully updated!")
    return jsonify(
        {
            "success": True,
            "url": url_for(f"{BlueprintName.PROFILE.value}.therapist_profile"),
        }
    )


@bp.route("/client/profile", methods=["GET", "POST"])
@login_required
@client_required
def client_profile():
    form = ClientProfileForm()

    # GET request - display page
    if request.method == "GET":
        return render_template("client_profile.html", form=form)

    # POST request - validate form
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Insert client's information
    client = Client(
        user_id=current_user.id,
        preferred_gender=form.preferred_gender.data,
        preferred_language_id=form.preferred_language.data,
    )
    db.session.add(client)
    db.session.commit()

    # Insert client's issues
    client_issues = form.issues.get_association_data(
        parent_id=client.id, parent_key="client_id", child_key="issue_id"
    )
    db.session.execute(client_issue.insert(), client_issues)

    # Insert client's session formats
    client_formats = form.session_formats.get_association_data(
        parent_id=client.id, parent_key="client_id", child_key="session_format_id"
    )
    db.session.execute(client_format.insert(), client_formats)

    db.session.commit()

    # Successful update - reload page
    flash("Client profile information successfully updated!")
    return jsonify(
        {
            "success": True,
            "url": url_for(f"{BlueprintName.PROFILE.value}.client_profile"),
        }
    )
