from flask import Blueprint, flash, jsonify, render_template, request, url_for
from flask_login import current_user, login_required

from app import BlueprintName, db
from app.forms.profile import ClientProfileForm, TherapistProfileForm
from app.models.client import Client
from app.models.issue import Issue
from app.models.language import Language
from app.models.session_format import SessionFormatModel
from app.models.therapist import Therapist
from app.utils.decorators import client_required, therapist_required

bp = Blueprint(BlueprintName.PROFILE.value, __name__)


@bp.route("/therapist/profile", methods=["GET", "POST"])
@login_required
@therapist_required
def therapist_profile():
    therapist = current_user.therapist

    # GET request - display page
    if request.method == "GET":
        form = TherapistProfileForm(obj=therapist)

        # Preselect therapist's existing profile data
        if therapist:
            form.languages.preselect_choices(therapist.languages)
            form.issues.preselect_choices(therapist.specialisations)
            form.session_formats.preselect_choices(therapist.session_formats)

        return render_template("therapist_profile.html", form=form)

    # POST request - validate form
    form = TherapistProfileForm()
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update therapist's profile data if it exists
    if therapist:
        therapist.gender = form.gender.data
        therapist.country = form.country.data
        therapist.affiliation = form.affiliation.data
        therapist.bio = form.bio.data
        therapist.link = form.link.data
        therapist.location = form.location.data
        therapist.years_of_experience = form.years_of_experience.data
        therapist.registrations = form.registrations.data
        therapist.qualifications = form.qualifications.data

    # Insert new data if no profile exists
    else:
        therapist = Therapist(
            user_id=current_user.id,
            gender=form.gender.data,
            country=form.country.data,
            affiliation=form.affiliation.data,
            bio=form.bio.data,
            link=form.link.data,
            location=form.location.data,
            years_of_experience=form.years_of_experience.data,
            registrations=form.registrations.data,
            qualifications=form.qualifications.data,
        )
        db.session.add(therapist)
    db.session.commit()

    # Update therapist's languages
    form.languages.update_association_data(
        parent=therapist, child=Language, children="languages"
    )

    # Update therapist's specialisations (issues)
    form.issues.update_association_data(
        parent=therapist, child=Issue, children="specialisations"
    )

    # Update therapist's session formats
    form.session_formats.update_association_data(
        parent=therapist, child=SessionFormatModel, children="session_formats"
    )

    db.session.commit()

    # Successful update - reload page
    flash("Profile information updated!")
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
    client = current_user.client

    # GET request - display page
    if request.method == "GET":
        form = ClientProfileForm(obj=client)

        # Preselect therapist's existing profile data
        if client:
            form.preferred_language.preselect_choices(client.preferred_language)
            form.preferred_gender.preselect_choices(client.preferred_gender)
            form.issues.preselect_choices(client.issues)
            form.session_formats.preselect_choices(client.session_formats)

        return render_template("client_profile.html", form=form)

    # POST request - validate form
    form = ClientProfileForm()
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update client's profile data if it exists
    if client:
        client.preferred_gender = form.preferred_gender.data
        client.preferred_language_id = form.preferred_language.data

    # Insert new data if no profile exists
    else:
        client = Client(
            user_id=current_user.id,
            preferred_gender=form.preferred_gender.data,
            preferred_language_id=form.preferred_language.data,
        )
        db.session.add(client)
    db.session.commit()

    # Update client's issues
    form.issues.update_association_data(parent=client, child=Issue, children="issues")

    # Update client's session formats
    form.session_formats.update_association_data(
        parent=client, child=SessionFormatModel, children="session_formats"
    )

    db.session.commit()

    # Successful update - reload page
    flash("Profile information updated!")
    return jsonify(
        {
            "success": True,
            "url": url_for(f"{BlueprintName.PROFILE.value}.client_profile"),
        }
    )
