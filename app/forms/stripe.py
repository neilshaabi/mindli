from wtforms import SubmitField

from app.forms import CustomFlaskForm


class CreateStripeAccountForm(CustomFlaskForm):
    submit = SubmitField("Stripe Onboarding")
