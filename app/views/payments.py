import stripe
from flask import Blueprint, jsonify, render_template, request

bp = Blueprint("payments", __name__, url_prefix="/payments")


@bp.route("/setup", methods=["GET"])
def setup_payments():
    return render_template("setup_payments.html")


@bp.route("/account_session", methods=["POST"])
def create_account_session():
    try:
        connected_account_id = request.get_json().get("account")

        account_session = stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "account_onboarding": {"enabled": True},
            },
        )

        return jsonify(
            {
                "client_secret": account_session.client_secret,
            }
        )
    except Exception as e:
        print(
            "An error occurred when calling the Stripe API to create an account session: ",
            e,
        )
        return jsonify(error=str(e)), 500


@bp.route("/account", methods=["POST"])
def create_account():
    try:
        account = stripe.Account.create(
            type="standard",
        )

        return jsonify(
            {
                "account": account.id,
            }
        )
    except Exception as e:
        print("An error occurred when calling the Stripe API to create an account: ", e)
        return jsonify(error=str(e)), 500
