import secrets

import stripe
from flask import (Blueprint, abort, current_app, flash, json, jsonify,
                   redirect, request, session, url_for)
from flask_login import current_user, login_required

from app import csrf, db
from app.models.appointment import Appointment
from app.models.enums import EmailSubject, PaymentStatus
from app.utils.decorators import therapist_required
from app.utils.mail import send_appointment_update_email

bp = Blueprint("stripe", __name__, url_prefix="/stripe")


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
                "name": current_user.full_name,
                "mcc": "8099",  # Medical Services
                "product_description": "Mindli provides online psychotherapy services, connecting mental health practioners with clients for support. Services include individual, couples and family therapy sessions.",
            },
        )

        # Store state in session for verification in /return endpoint
        session["stripe_onboarding_state"] = secrets.token_urlsafe()

        account_link = stripe.AccountLink.create(
            account=account.id,
            type="account_onboarding",
            refresh_url=url_for("stripe.stripe_refresh", _external=True),
            return_url=url_for(
                "stripe.stripe_return",
                account_id=account.id,
                state=session["stripe_onboarding_state"],
                _external=True,
            ),
        )

    # Error creating Stripe account
    except Exception as e:
        flash("Failed to initiate Stripe onboarding: " + str(e), "error")
        return jsonify(
            {
                "success": False,
                "errors": {"submit": [f"Error creating Stripe account: {str(e)}"]},
                "url": url_for(
                    "therapists.therapist",
                    therapist_id=current_user.therapist.id,
                    section="payments",
                ),
            }
        )

    # Redirect user to Stripe-hosted onboarding
    return jsonify({"success": True, "url": account_link.url})


@bp.route("/refresh", methods=["GET"])
@login_required
@therapist_required
def stripe_refresh():
    flash(
        "Stripe onboarding unsuccessful",
        "warning",
    )
    return redirect(
        url_for(
            "therapists.therapist",
            therapist_id=current_user.therapist.id,
            section="payments",
            _external=True,
        )
    )


@bp.route("/return", methods=["GET"])
@login_required
@therapist_required
def stripe_return():
    # Verify user returned from Stripe onboarding flow
    if not request.args.get("state") or request.args.get("state") != session.pop(
        "stripe_onboarding_state", None
    ):
        abort(403)

    # Retrieve account via Stripe API
    account_id = request.args.get("account_id")
    account = stripe.Account.retrieve(account_id)

    # Stripe onboarding incomplete - redirect
    if not account.details_submitted or not account.charges_enabled:
        flash(
            "Stripe onboarding incomplete",
            "warning",
        )
        return redirect(
            url_for(
                "therapists.therapist",
                therapist_id=current_user.therapist.id,
                section="payments",
                _external=True,
            )
        )

    # Update therapist's stripe account ID in database
    current_user.therapist.stripe_account_id = account_id
    db.session.commit()

    # Successfully completed onboarding
    flash(
        "Stripe onboarding completed",
        "success",
    )
    return redirect(
        url_for(
            "therapists.therapist",
            therapist_id=current_user.therapist.id,
            section="payments",
        )
    )


@bp.route("/webhook", methods=["POST"])
@csrf.exempt
def webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")

    # Retrieve your Stripe webhook secret from your configuration
    webhook_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")

    if webhook_secret:
        # Verify the webhook signature and construct the event
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError as e:
            # Invalid payload
            print("Invalid payload", str(e))
            return jsonify(success=False), 400
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print("Invalid signature", str(e))
            return jsonify(success=False), 400
        except Exception as e:
            # Other unexpected error
            print("Webhook error", str(e))
            return jsonify(success=False), 400
    else:
        # Webhook secret not provided in configuration, handle event as unverified
        try:
            event = json.loads(payload)
        except json.decoder.JSONDecodeError as e:
            print("Webhook error while parsing basic request." + str(e))
            return jsonify(success=False), 400

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if session.payment_status == "paid":
            handle_payment_succeeded(session)
    elif event["type"] == "checkout.session.async_payment_succeeded":
        handle_payment_succeeded(event["data"]["object"])
    elif event["type"] == "checkout.session.async_payment_failed":
        handle_payment_failed(event["data"]["object"])
    else:
        print(f"Unhandled event type {event['type']}")

    return jsonify(success=True), 200


def handle_payment_succeeded(session: stripe.checkout.Session):
    # Fetch the appointment using the ID included in the session metadata
    appointment_id = session.get("metadata").get("appointment_id")
    appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Return if appointment has already been updated
    if appointment.payment_status == PaymentStatus.SUCCEEDED:
        return

    # Update the appointment's payment status in the database
    appointment.payment_status = PaymentStatus.SUCCEEDED
    db.session.commit()

    # Send email to client
    send_appointment_update_email(
        appointment=appointment,
        recipient=appointment.client.user,
        subject=EmailSubject.APPOINTMENT_CANCELLED,
    )

    # Send email to therapist
    send_appointment_update_email(
        appointment=appointment,
        recipient=appointment.therapist.user,
        subject=EmailSubject.APPOINTMENT_CANCELLED,
    )
    return


def handle_payment_failed(session: stripe.checkout.Session):
    # Fetch the appointment using the ID included in the session metadata
    appointment_id = session.get("metadata").get("appointment_id")
    appointment = db.session.execute(
        db.select(Appointment).filter_by(id=appointment_id)
    ).scalar_one()

    # Return if appointment has already been updated
    if appointment.payment_status == PaymentStatus.SUCCEEDED:
        return

    # Update the appointment's payment status in the database
    appointment.payment_status = PaymentStatus.FAILED
    db.session.commit()

    # Send email to client
    send_appointment_update_email(
        appointment=appointment,
        recipient=appointment.client.user,
        subject=EmailSubject.PAYMENT_FAILED_CLIENT,
    )
    return


def create_checkout_session(appointment: Appointment) -> str:
    try:
        # Convert fee amount to cents for Stripe
        unit_amount = int(appointment.appointment_type.fee_amount * 100)

        # Create checkout session via Stripe API
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],  # You can specify more methods if needed
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": appointment.appointment_type.fee_currency.lower(),
                        "product_data": {
                            "name": f"Appointment with {appointment.therapist.user.full_name} - {appointment.appointment_type.therapy_type.value}, {appointment.appointment_type.therapy_mode.value} ({appointment.appointment_type.duration} minutes)"
                        },
                        "unit_amount": unit_amount,
                    },
                    "quantity": 1,
                },
            ],
            customer_email=current_user.email,
            stripe_account=appointment.therapist.stripe_account_id,
            success_url=url_for(
                "appointments.appointment",
                appointment_id=appointment.id,
                _external=True,
            ),
            cancel_url=url_for(
                "appointments.appointment",
                appointment_id=appointment.id,
                _external=True,
            ),
            metadata={"appointment_id": appointment.id},
        )
        return checkout_session.url

    except Exception as e:
        print(f"Stripe error: {e}")
        return None
