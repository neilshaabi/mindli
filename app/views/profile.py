import os

from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.forms.profile import ClientProfileForm, UserProfileForm
from app.models.client import Client
from app.models.enums import UserRole
from app.models.issue import Issue
from app.utils.decorators import client_required
from app.utils.files import get_file_extension
from app.utils.formatters import get_flashed_message_html

bp = Blueprint("profile", __name__, url_prefix="/profile")


@bp.route("/", methods=["GET"])
@login_required
def index():
    if current_user.role == UserRole.THERAPIST:
        if current_user.therapist:
            return redirect(
                url_for("therapists.therapist", therapist_id=current_user.therapist.id)
            )
        else:
            return redirect(url_for("therapists.new_therapist"))

    elif current_user.role == UserRole.CLIENT:
        if current_user.client:
            return redirect(
                url_for("clients.client", therapist_id=current_user.therapist.id)
            )
        else:
            return redirect(url_for("clients.new_client"))

    else:
        print("Unhandled user role")
        return redirect(url_for("main.index"))


@bp.route("/profile/user", methods=["POST"])
@login_required
def user_profile():
    # Generate form for personal information common to all users
    form = UserProfileForm()

    # Invalid form submission - return errors
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors})

    # Handle profile picture upload
    file = request.files.get("profile_picture")
    if file:
        extension = get_file_extension(file)
        filename = secure_filename(f"user_{current_user.id}.{extension}")
        filepath = os.path.join("static", "img", "profile_pictures", filename)
        savepath = os.path.join(current_app.root_path, filepath)
        file.save(savepath)
        current_user.profile_picture = filename

    # Update user's data
    current_user.first_name = form.first_name.data
    current_user.last_name = form.last_name.data
    current_user.gender = form.gender.data
    db.session.commit()

    # Flash message using AJAX
    return jsonify(
        {
            "success": True,
            "flashed_message_html": get_flashed_message_html(
                "Personal information updated", "success"
            ),
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

    client = current_user.client

    # Update client's profile if it exists
    if client:
        client.date_of_birth = form.date_of_birth.data
        client.occupation = form.occupation.data
        client.address = form.address.data
        client.phone = form.phone.data
        client.emergency_contact_name = form.emergency_contact_name.data
        client.emergency_contact_phone = form.emergency_contact_phone.data
        client.referral_source = form.referral_source.data

    # Insert new data if no profile exists
    else:
        client = Client(
            user_id=current_user.id,
            date_of_birth=form.date_of_birth.data,
            occupation=form.occupation.data,
            address=form.address.data,
            phone=form.phone.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            referral_source=form.referral_source.data,
        )
        db.session.add(client)
    db.session.commit()

    # Update client's issues
    form.issues.update_association_data(parent=client, child=Issue, children="issues")

    db.session.commit()

    # Flash message using AJAX
    return jsonify(
        {
            "success": True,
            "flashed_message_html": get_flashed_message_html(
                "Background information updated", "success"
            ),
        }
    )
