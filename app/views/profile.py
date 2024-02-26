from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Client, Therapist
from app.models.enums import UserRole

# Assuming 'profile_bp' is your Blueprint
profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    if request.method == "POST":
        if current_user.role == UserRole.THERAPIST:
            # Process form data for therapist profile setup
            bio = request.form.get("bio")
            qualifications = request.form.get("qualifications")
            years_of_experience = request.form.get("years_of_experience")
            # Additional fields as needed

            if (
                not bio or not qualifications or not years_of_experience
            ):  # Basic validation
                flash("Please fill out all required fields.", "error")
                return redirect(url_for("profile.setup"))

            therapist = Therapist(
                user_id=current_user.id,
                bio=bio,
                qualifications=qualifications,
                years_of_experience=int(years_of_experience)
                # Set other fields as needed
            )
            db.session.add(therapist)
            db.session.commit()
            flash("Profile setup complete.", "success")
            return redirect(url_for("dashboard"))

        elif current_user.role == UserRole.CLIENT:
            # Process form data for client profile setup
            preferred_gender = request.form.get("preferred_gender")
            # Additional fields as needed

            if not preferred_gender:  # Basic validation
                flash("Please fill out all required fields.", "error")
                return redirect(url_for("profile.setup"))

            client = Client(
                user_id=current_user.id,
                preferred_gender=preferred_gender
                # Set other fields as needed
            )
            db.session.add(client)
            db.session.commit()
            flash("Profile setup complete.", "success")
            return redirect(url_for("dashboard"))

    # GET request or if the user's role doesn't match
    return render_template("profile_setup.html")
