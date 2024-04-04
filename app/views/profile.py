import os

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import BlueprintName, db
from app.forms.profile import ClientProfileForm, TherapistProfileForm, UserProfileForm
from app.models.client import Client
from app.models.enums import UserRole
from app.models.issue import Issue
from app.models.language import Language
from app.models.session_format import SessionFormatModel
from app.models.therapist import Therapist
from app.utils.decorators import client_required, therapist_required
from app.utils.files import get_file_extension

bp = Blueprint(BlueprintName.PROFILE.value, __name__)


@bp.route("/profile", methods=["GET"])
@login_required
def profile():
    # Generate form for personal information common to all users
    user_form = UserProfileForm(obj=current_user)
    user_form.gender.preselect_choices(current_user.gender)

    # Declare forms for specific roles
    therapist_form = None
    client_form = None

    if current_user.role == UserRole.THERAPIST:
        # Generate form for therapist's professional information
        therapist = current_user.therapist
        therapist_form = TherapistProfileForm(obj=therapist)

        # Preselect data from therapist's profile if it exists
        if therapist:
            therapist_form.languages.preselect_choices(therapist.languages)
            therapist_form.issues.preselect_choices(therapist.specialisations)
            therapist_form.session_formats.preselect_choices(therapist.session_formats)

    elif current_user.role == UserRole.CLIENT:
        # Generate form for client's preferences
        client = current_user.client
        client_form = ClientProfileForm(obj=client)

        # Preselect data from client's profile if it exists
        if client:
            client_form.preferred_language.preselect_choices(client.preferred_language)
            client_form.preferred_gender.preselect_choices(client.preferred_gender)
            client_form.issues.preselect_choices(client.issues)
            client_form.session_formats.preselect_choices(client.session_formats)

    return render_template(
        "profile.html",
        UserRole=UserRole,
        user_form=user_form,
        therapist_form=therapist_form,
        client_form=client_form,
    )


@bp.route("/profile/user", methods=["POST"])
@login_required
def user_profile():
    form = UserProfileForm()
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update user's data
    current_user.first_name = form.first_name.data
    current_user.last_name = form.last_name.data
    current_user.gender = form.gender.data

    # Handle profile picture upload
    file = request.files.get("profile_picture")
    if file:
        extension = get_file_extension(file)
        filename = secure_filename(f"user_{current_user.id}.{extension}")
        filepath = os.path.join("static", "img", "profile_pictures", filename)
        savepath = os.path.join(current_app.root_path, filepath)
        file.save(savepath)
        current_user.profile_picture = filename

    db.session.commit()

    # Reload page
    flash("Personal information updated")
    return jsonify(
        {"success": True, "url": url_for(f"{BlueprintName.PROFILE.value}.profile")}
    )


@bp.route("/profile/therapist", methods=["POST"])
@login_required
@therapist_required
def therapist_profile():
    therapist = current_user.therapist

    # POST request - validate form
    form = TherapistProfileForm()
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update therapist's profile if it exists
    if therapist:
        therapist.country = form.country.data
        therapist.bio = form.bio.data
        therapist.link = form.link.data
        therapist.location = form.location.data
        therapist.years_of_experience = form.years_of_experience.data
        therapist.qualifications = form.qualifications.data
        therapist.registrations = form.registrations.data

    # Insert new data if no profile exists
    else:
        therapist = Therapist(
            user_id=current_user.id,
            country=form.country.data,
            bio=form.bio.data,
            link=form.link.data,
            location=form.location.data,
            years_of_experience=form.years_of_experience.data,
            qualifications=form.qualifications.data,
            registrations=form.registrations.data,
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

    # Reload page
    flash("Professional information updated")
    return jsonify(
        {
            "success": True,
            "url": url_for(f"{BlueprintName.PROFILE.value}.profile"),
        }
    )


@bp.route("/profile/client", methods=["POST"])
@login_required
@client_required
def client_profile():
    client = current_user.client

    # POST request - validate form
    form = ClientProfileForm()
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Convert form's default values to None
    if form.preferred_gender.data == "":
        form.preferred_gender.data = None
    if form.preferred_language.data == 0:
        form.preferred_language.data = None

    # Update client's profile if it exists
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

    # Reload page
    flash("Client preferences updated")
    return jsonify(
        {
            "success": True,
            "url": url_for(f"{BlueprintName.PROFILE.value}.profile"),
        }
    )
