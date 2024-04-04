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


@bp.route("/profile/user", methods=["POST"])
@login_required
def profile():
    # POST request - validate form
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
    if current_user.role == UserRole.THERAPIST:
        redirect_url = url_for(f"{BlueprintName.PROFILE.value}.therapist_profile")
    else:
        redirect_url = url_for(f"{BlueprintName.PROFILE.value}.client_profile")

    return jsonify({"success": True, "url": redirect_url})


@bp.route("/profile/therapist", methods=["GET", "POST"])
@login_required
@therapist_required
def therapist_profile():
    therapist = current_user.therapist

    # GET request - display page
    if request.method == "GET":
        # Preselect existing user data
        user_profile_form = UserProfileForm(obj=current_user)
        user_profile_form.gender.preselect_choices(current_user.gender)

        # Preselect existing therapist profile data
        therapist_profile_form = TherapistProfileForm(obj=therapist)
        if therapist:
            therapist_profile_form.languages.preselect_choices(therapist.languages)
            therapist_profile_form.issues.preselect_choices(therapist.specialisations)
            therapist_profile_form.session_formats.preselect_choices(
                therapist.session_formats
            )

        return render_template(
            "therapist_profile.html",
            user_profile_form=user_profile_form,
            therapist_profile_form=therapist_profile_form,
        )

    # POST request - validate form
    form = TherapistProfileForm()
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Update therapist's profile data if it exists
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
            "url": url_for(f"{BlueprintName.PROFILE.value}.therapist_profile"),
        }
    )


@bp.route("/profile/client", methods=["GET", "POST"])
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

    # Convert default values to None
    if form.preferred_gender.data == "":
        form.preferred_gender.data = None
    if form.preferred_language.data == 0:
        form.preferred_language.data = None

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

    # Reload page
    flash("Profile information updated")
    return jsonify(
        {
            "success": True,
            "url": url_for(f"{BlueprintName.PROFILE.value}.client_profile"),
        }
    )
