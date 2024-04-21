import stripe
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.stripe import CreateStripeAccountForm
from app.utils.decorators import therapist_required

bp = Blueprint("stripe", __name__, url_prefix="/stripe")


@bp.route("/", methods=["GET"])
@login_required
@therapist_required
def stripe_entry():
    form = CreateStripeAccountForm(
        id="create_stripe_account",
        endpoint=url_for("stripe.create_account"),
    )
    return render_template("stripe.html", form=form)


@bp.route("/create-account", methods=["POST"])
@login_required
@therapist_required
def create_account():
    # Call Stripe APIs to create and link account
    try:
        account = stripe.Account.create(
            type="standard",
            business_type="individual",
            email=current_user.email,
            business_profile={
                "name": f"{current_user.first_name} {current_user.first_name}",
                "mcc": "8099",  # Medical Services
                "url": url_for(
                    "therapist_directory.therapist",
                    therapist_id=current_user.therapist.id,
                    _external=True,
                ),
            },
        )

        account_link = stripe.AccountLink.create(
            account=account.id,
            type="account_onboarding",
            refresh_url=url_for("stripe.refresh", _external=True),
            return_url=url_for(
                "stripe.stripe_return", account_id=account.id, _external=True
            ),
        )

    # Error creating Stripe account
    except Exception as e:
        return jsonify({"success": False, "errors": {"submit": [str(e)]}})

    flash("Please follow the link to complete your Stripe onboarding", "info")
    return jsonify({"success": True, "url": account_link.url})


@bp.route("/refresh")
@login_required
@therapist_required
def refresh():
    flash(
        "Your session has expired, please start the Stripe onboarding process again",
        "warning",
    )
    return redirect(url_for("stripe.stripe_entry"))


@bp.route("/return", methods=["GET"])
@login_required
@therapist_required
def stripe_return():
    # Retrieve account via Stripe API
    account_id = request.args.get("account_id")
    account = stripe.Account.retrieve(account_id)

    # Handle incomplete Stripe onboarding
    if not account.details_submitted or not account.charges_enabled:
        # Generate a new link for the user to continue their onboarding
        try:
            flash(
                "Your Stripe onboarding is incomplete, please complete the required steps",
                "warning",
            )
            account_link = stripe.AccountLink.create(
                account=account_id,
                type="account_onboarding",
                refresh_url=url_for("stripe.refresh", _external=True),
                return_url=url_for(
                    "stripe.stripe_return", account_id=account_id, _external=True
                ),
            )
            return redirect(account_link.url)

        except Exception as e:
            flash("Failed to generate a new Stripe onboarding link: " + str(e), "error")
            return redirect(url_for("stripe.stripe_entry"))

    # Successfully completed onboarding
    flash(
        "Your Stripe onboarding is complete, and you can now receive payments",
        "success",
    )
    return render_template("onboarding_complete.html")
