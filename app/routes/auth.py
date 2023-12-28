from datetime import date

from flask import (
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from markupsafe import escape
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db, mail, serialiser
from app.db import User
from app.utils import isValidPassword, sendEmailWithToken


# Logs user out
@app.route("/logout")
def logout() -> Response:
    session.clear()
    logout_user()
    return redirect("/")


# Allows users to register for an account
@app.route("/register", methods=["GET", "POST"])
def register() -> Response:
    if request.method == "POST":
        # Get form data
        first_name = escape(request.form.get("first_name"))
        last_name = escape(request.form.get("last_name"))
        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure full name was entered
        if (not first_name or first_name.isspace()) or (
            not last_name or last_name.isspace()
        ):
            error = "Please enter your full name"

        # Ensure email was entered
        elif not email or email.isspace():
            error = "Please enter your email"

        # Ensure user with same email does not already exist
        elif User.query.filter_by(email=email.lower()).first() is not None:
            error = "This email address is already in use"

        # Ensure a valid password was entered
        elif not isValidPassword(password):
            error = "Please enter a valid password"

        # Successful registration
        else:
            # Insert new user into database
            email = email.lower()
            user = User(
                email,
                generate_password_hash(password),
                first_name.capitalize(),
                last_name.capitalize(),
                date.today(),
                None,
                None,
                False,
                False,
                None,
            )
            db.session.add(user)
            db.session.commit()

            # Send verification email and redirect to home page
            sendEmailWithToken(
                serialiser, mail, user.first_name, user.email, "Email Verification"
            )
            session["email"] = email
            return url_for("verify_email")

        return jsonify({"error": error})

    # Request method is GET
    else:
        logout_user()
        return render_template("register.html")


# Logs user in if credentials are valid
@app.route("/login", methods=["GET", "POST"])
def login() -> Response:
    if request.method == "POST":
        # Get form data
        email = request.form.get("email").lower()
        password = request.form.get("password")

        # Find user with this email
        user = User.query.filter_by(email=email).first()

        # Check if user with this email does not exist or if password is incorrect
        if user is None or not check_password_hash(user.password_hash, password):
            error = "Incorrect email/password"

        # Check if user's email has been verified
        elif not user.verified:
            session["email"] = email
            return url_for("verify_email")

        # Log user in and redirect to home page
        else:
            login_user(user)
            current_user.is_exec = (
                User.query.with_entities(User.is_exec)
                .filter_by(id=current_user.id)
                .first()[0]
            )
            return url_for("index")

        return jsonify({"error": error})

    # Request method is GET
    else:
        logout_user()
        return render_template("login.html")


# Displays page with email verification instructions, sends verification email
@app.route("/verify-email", methods=["GET", "POST"])
def verify_email() -> Response:
    # Get user with email stored in session
    user = (
        User.query.filter_by(email=session["email"]).first()
        if "email" in session
        else None
    )

    # Redirect if the email address is invalid or already verified
    if not user or user.verified:
        return redirect("/")

    # Sends verification email to user (POST used to utilise AJAX)
    if request.method == "POST":
        sendEmailWithToken(
            serialiser, mail, user.first_name, user.email, "Email Verification"
        )
        return ""
    else:
        return render_template("verify-email.html", email=session["email"])


# Directed to by link in verification emails, handles email verification using token
@app.route("/email-verification/<token>")
def email_verification(token):
    # Get email from token
    try:
        email = serialiser.loads(
            token, max_age=86400
        )  # Each token is valid for 24 hours

        # Mark user as verified
        user = User.query.filter_by(email=email).first()
        user.verified = True
        db.session.commit()

        # Log in user
        login_user(user)
        flash("Success! Your email address has been verified")

    # Invalid/expired token
    except:
        flash(
            "Invalid or expired verification link, please sign in to request a new link"
        )

    return redirect("/")


# Handles password resets by sending emails and updating the database
@app.route("/reset-password", methods=["GET", "POST"])
def reset_request() -> Response:
    if request.method == "POST":
        # Form submitted to request a password reset
        if request.form.get("form-type") == "request":
            # Get form data
            email = request.form.get("email").lower()

            # Find user with this email
            user = User.query.filter_by(email=email).first()

            # Check if user with this email does not exist
            if user is None:
                error = "No account found with this email address"

            # Send reset email
            else:
                sendEmailWithToken(
                    serialiser, mail, user.first_name, user.email, "Password Reset"
                )
                flash("Password reset instructions sent to {}".format(email))
                return url_for("index")

            return jsonify({"error": error})

        # Form submitted to reset password
        elif request.form.get("form-type") == "reset":
            # Get form data
            email = request.form.get("email")
            password = request.form.get("password")
            password_confirmation = request.form.get("password_confirmation")

            # Ensure a valid password was entered
            if not isValidPassword(password):
                error = "Please enter a valid password"

            # Ensure password and confirmation match
            elif password != password_confirmation:
                error = "Passwords do not match"

            # Successful reset
            else:
                # Update user's password in database
                user = User.query.filter_by(email=email).first()
                user.password_hash = generate_password_hash(password)
                db.session.commit()

                # Redirect to login page
                flash("Success! Your password has been reset")
                return url_for("index")

            return jsonify({"error": error})

    # Request method is GET
    else:
        return render_template("reset-request.html")


# Directed to by link in password reset emails, displays page to update password
@app.route("/reset-password/<token>")
def reset_password(token):
    # Get email from token
    try:
        email = serialiser.loads(
            token, max_age=86400
        )  # Each token is valid for 24 hours
        return render_template("reset-password.html", email=email)

    # Invalid/expired token
    except:
        flash("Invalid or expired reset link, please request another password reset")
        return redirect("/")
