from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

from app.models.enums import UserRole


def profile_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if getattr(current_user, current_user.role.value) is None:
                flash(
                    "Please complete your profile to access all available features",
                    "warning",
                )
                return redirect(url_for("profile.profile"))
        return f(*args, **kwargs)

    return decorated_function


def therapist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != UserRole.THERAPIST:
            flash("You are not authorised to view this page", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


def client_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != UserRole.CLIENT:
            flash("You are not authorised to view this page", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function
