from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

from app import BlueprintName


def profile_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if getattr(current_user, current_user.role.value) is None:
                flash("Please complete your profile to access all available features")
                return redirect(url_for(f"{BlueprintName.PROFILE.value}.profile"))
        return f(*args, **kwargs)

    return decorated_function
