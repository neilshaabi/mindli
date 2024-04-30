import os

from flask import (Blueprint, Response, abort, current_app, flash, jsonify,
                   request, url_for)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.forms.users import UserProfileForm
from app.utils.files import get_file_extension

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/<int:user_id>", methods=["POST"])
@login_required
def update(user_id: int) -> Response:
    # Current user is not authorised
    if user_id != current_user.id:
        abort(403)

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

        filepath = os.path.join("app", "static", "img", "profile_pictures", filename)
        savepath = os.path.join(current_app.root_path, filepath)
        file.save(savepath)
        current_user.profile_picture = filename

    # Update user's data
    current_user.first_name = form.first_name.data
    current_user.last_name = form.last_name.data
    current_user.gender = form.gender.data
    db.session.commit()

    flash("Personal information updated", "success")
    return jsonify(
        {
            "success": True,
            "url": url_for("profile.profile", user_id=current_user.id),
        }
    )
