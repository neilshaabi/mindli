from datetime import date

from flask import (Blueprint, Response, current_app, flash, jsonify, redirect,
                   render_template, request, session, url_for)
from flask_login import login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, mail
from app.models import User, UserRole
from app.utils.mail import EmailMessage, EmailSubject
from app.utils.password import isValidPassword

bp = Blueprint("auth", __name__)


@bp.route("/")
@bp.route("/index")
def index() -> Response:
    return render_template("index.html")


@bp.route("/logout")
def logout() -> Response:
    session.clear()
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register() -> Response:
    
    if request.method == "POST":
        
        errors = {}

        # Get form data
        role = request.form.get("role")
        first_name = escape(request.form.get("first_name"))
        last_name = escape(request.form.get("last_name"))
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate input
        if not role:
            errors["role"] = "Account type is required"
        if not first_name or first_name.isspace():
            errors["first_name"] = "First name is required"
        if not last_name or last_name.isspace():
            errors["last_name"] = "Last name is required"
        if not email or email.isspace():
            errors["email"] = "Email is required"
        elif User.query.filter_by(email=email.lower()).first():
            errors["email"] = "Email address is already in use"
        if not isValidPassword(password):
            errors["password"] = "Password does not meet requirements"
        if errors:
            return jsonify({"errors": errors})

        # Proceed with successful registration
        else:
            # Insert new user into database
            email = email.lower()
            user = User(
                email=email.lower(),
                password_hash=generate_password_hash(password),
                first_name=first_name.capitalize(),
                last_name=last_name.capitalize(),
                date_joined=date.today(),
                role=UserRole(role),
                verified=False,
                active=True,
            )
            db.session.add(user)
            db.session.commit()

            # Send verification email and redirect
            email_message = EmailMessage(
                mail=mail,
                subject=EmailSubject.EMAIL_VERIFICATION,
                recipient=user,
                serialiser=current_app.serialiser,
            )
            email_message.send()
            session["email"] = email
            return jsonify({"url": url_for("auth.verify_email")})

    # Request method is GET
    else:
        logout_user()
        return render_template("register.html")


# Logs user in if credentials are valid
@bp.route("/login", methods=["GET", "POST"])
def login() -> Response:
    if request.method == "POST":
        errors = {}

        # Get form data
        email = request.form.get("email").lower()
        password = request.form.get("password")

        # Validate input
        if not email:
            errors["email"] = "Email is required"
        if not password:
            errors["password"] = "Password is required"
        else:
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
            if user is None or not check_password_hash(user.password_hash, password):
                errors["password"] = "Incorrect email/password"
        if errors:
            return jsonify({"errors": errors})

        # Ensure user's email is verified
        if not user.verified:
            # Store email in session for verification and redirect
            session["email"] = email
            return jsonify({"url": url_for("auth.verify_email")})

        # Log user in and redirect to home page
        login_user(user)
        return jsonify({"url": url_for("main.index")})

    # Request method is GET
    else:
        logout_user()
        return render_template("login.html")


# Displays page with email verification instructions, sends verification email
@bp.route("/verify-email", methods=["GET", "POST"])
def verify_email() -> Response:
    
    # Get user with email stored in session
    if "email" in session:
        user = db.session.execute(db.select(User).filter_by(email=session["email"])).scalar_one_or_none()
    else:
        user = None

    # Redirect if the email address is invalid or already verified
    if not user or user.verified:
        return redirect(url_for("main.index"))

    # Sends verification email to user (POST used to utilise AJAX)
    if request.method == "POST":
        email_message = EmailMessage(
            mail=mail,
            subject=EmailSubject.EMAIL_VERIFICATION,
            recipient=user,
            serialiser=current_app.serialiser,
        )
        email_message.send()
        flash(f"Email verification instructions sent to {user.email}")
        return jsonify({"url": url_for("main.index")})
    
    else:
        return render_template("verify-email.html", email=session["email"])


# Handles email verification using token
@bp.route("/email-verification/<token>")
def email_verification(token):
    
    # Get email from token
    try:
        email = current_app.serialiser.loads(
            token, max_age=(60 * 60 * 24 * 5)
        )  # Each token is valid for 5 days

        # Mark user as verified
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        user.verified = True
        db.session.commit()

        # Log in user
        login_user(user)
        flash("Success! Your email address has been verified")

    # Invalid/expired token
    except (BadSignature, SignatureExpired):
        flash(
            "Invalid or expired verification link, "
            "please log in to request a new link"
        )
    
    return redirect(url_for("main.index"))


# Handles password resets by sending emails and updating the database
@bp.route("/reset-password", methods=["GET", "POST"])
def reset_request() -> Response:
    if request.method == "POST":
        
        errors = {}
        
        # Form submitted to initiate a password reset
        if request.form.get("form-type") == "initiate_password_reset":
            
            # Get form data
            email = request.form.get("email").lower()

            # Find user with this email
            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()

            # Check if user with this email does not exist
            if user is None:
                errors["email"] = "No account found with this email address"

            # Return errors if any
            if errors:
                return jsonify({"errors": errors})
            
            # Send reset email
            else:
                email_message = EmailMessage(
                    mail=mail,
                    subject=EmailSubject.PASSWORD_RESET,
                    recipient=user,
                    serialiser=current_app.serialiser,
                )
                email_message.send()
                flash(f"Password reset instructions sent to {email}")
                return jsonify({"url": url_for("main.index")})

        # Form submitted to reset password
        elif request.form.get("form-type") == "reset_password":
            
            # Get form data
            email = request.form.get("email")
            password = request.form.get("password")
            password_confirmation = request.form.get("password_confirmation")

            # Validate input
            if not isValidPassword(password):
                errors["password"] = "Password does not meet requirements"
            if not password_confirmation:
                errors["password_confirmation"] = "Password confirmation is required"
            elif password != password_confirmation:
                errors["password_confirmation"] = "Passwords do not match"
            if errors:
                return jsonify({"errors": errors})
            
            # Successful reset
            else:
                # Update user's password in database
                user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
                user.password_hash = generate_password_hash(password)
                db.session.commit()

                # Redirect to login page
                flash("Success! Your password has been reset")
                return jsonify({"url": url_for("main.index")})

    # Request method is GET
    else:
        return render_template("initiate-password-reset.html")


# Displays page to update password
@bp.route("/reset-password/<token>")
def reset_password(token):
    # Get email from token
    try:
        email = current_app.serialiser.loads(
            token, max_age=86400
        )  # Each token is valid for 24 hours
        return render_template("reset-password.html", email=email)

    # Invalid/expired token
    except (BadSignature, SignatureExpired):
        flash("Invalid or expired reset link, " "please request another password reset")
        return redirect(url_for("main.index"))
