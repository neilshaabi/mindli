from wtforms import SubmitField

from app.forms import CustomFlaskForm


class CreateStripeAccountForm(CustomFlaskForm):
    submit = SubmitField("Create Stripe Account")
