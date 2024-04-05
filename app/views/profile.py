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

from app import db
from app.forms.profile import ClientProfileForm, TherapistProfileForm, UserProfileForm
from app.models.client import Client
from app.models.enums import UserRole
from app.models.issue import Issue
from app.models.language import Language
from app.models.session_format import SessionFormatModel
from app.models.therapist import Therapist
from app.utils.decorators import client_required, therapist_required
from app.utils.files import get_file_extension

bp = Blueprint("profile", __name__)


@bp.route("/profile", methods=["GET"])
@login_required
def profile():
    user_form = UserProfileForm(
        obj=current_user,
        id="user-profile",
        endpoint=url_for("profile.user_profile"),
    )

    if current_user.role == UserRole.THERAPIST:
        role_form = TherapistProfileForm(
            obj=current_user.therapist,
            id="therapist-profile",
            endpoint=url_for("profile.therapist_profile"),
        )

    elif current_user.role == UserRole.CLIENT:
        role_form = ClientProfileForm(
            obj=current_user.client,
            id="client-profile",
            endpoint=url_for("profile.client_profile"),
        )

    return render_template(
        "profile.html", UserRole=UserRole, user_form=user_form, role_form=role_form
    )


@bp.route("/profile/user", methods=["POST"])
@login_required
def user_profile():
    # Generate form for personal information common to all users
    form = UserProfileForm()

    # Invalid form submission - return errors
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
    return jsonify({"success": True, "url": url_for("profile.profile")})


@bp.route("/profile/therapist", methods=["POST"])
@login_required
@therapist_required
def therapist_profile():
    # Generate form for therapist-specific information
    form = TherapistProfileForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    therapist = current_user.therapist
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
            "url": url_for("profile.profile"),
        }
    )


@bp.route("/profile/client", methods=["POST"])
@login_required
@client_required
def client_profile():
    # Generate form for client-specific information
    form = ClientProfileForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Convert form's default values to None
    if form.preferred_gender.data == "":
        form.preferred_gender.data = None
    if form.preferred_language.data == 0:
        form.preferred_language.data = None

    client = current_user.client

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
            "url": url_for("profile.profile"),
        }
    )
