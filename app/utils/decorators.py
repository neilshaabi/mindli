from functools import wraps

from flask import abort
from flask_login import current_user

from app.models.enums import UserRole


def therapist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != UserRole.THERAPIST:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def client_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != UserRole.CLIENT:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
