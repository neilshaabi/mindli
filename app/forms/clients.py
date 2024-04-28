from wtforms import BooleanField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.forms import CustomFlaskForm, CustomSelectField, CustomSelectMultipleField
from app.models.enums import Occupation, ReferralSource
from app.models.issue import Issue
from app.utils.validators import (
    DateBeforeToday,
    NotWhitespace,
    ValidName,
    ValidPhoneNumber,
)


class ClientProfileForm(CustomFlaskForm):
    date_of_birth = DateField(
        "Date of birth",
        validators=[DataRequired(), DateBeforeToday()],
    )
    occupation = CustomSelectField(
        "Occupation",
        choices=[("", "Select occupation")],
        default="",
        validators=[DataRequired()],
    )
    address = StringField(
        "Address", validators=[DataRequired(), NotWhitespace(), Length(min=1, max=255)]
    )
    phone = StringField("Phone Number", validators=[DataRequired(), ValidPhoneNumber()])
    emergency_contact_name = StringField(
        "Emergency contact name",
        validators=[
            DataRequired(),
            NotWhitespace(),
            ValidName(),
            Length(min=1, max=50),
        ],
    )
    emergency_contact_phone = StringField(
        "Emergency contact phone", validators=[DataRequired(), ValidPhoneNumber()]
    )
    referral_source = CustomSelectField(
        "Referral source",
        choices=[("", "Select referral source")],
        default="",
        validators=[DataRequired()],
    )
    issues = CustomSelectMultipleField(
        "Current challenges",
        validators=[DataRequired()],
        coerce=int,
    )
    consent = BooleanField(
        "I consent to the collection of my personal information for the purposes of coordinating care",
        validators=[DataRequired()],
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(ClientProfileForm, self).__init__(*args, **kwargs)

        self.occupation.populate_choices(Occupation)
        self.issues.populate_choices(Issue)
        self.referral_source.populate_choices(ReferralSource)

        client = kwargs.get("obj")
        if client:
            self.occupation.preselect_choices(client.occupation)
            self.issues.preselect_choices(client.issues)
            self.referral_source.preselect_choices(client.referral_source)
        return
