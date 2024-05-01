from wtforms import (BooleanField, DateField, IntegerField, StringField,
                     SubmitField)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.forms import (CustomFlaskForm, CustomSelectField,
                       CustomSelectMultipleField)
from app.models.enums import Gender, Occupation, ReferralSource
from app.models.issue import Issue
from app.utils.validators import (DateBeforeToday, NotWhitespace,
                                  ValidPhoneNumber)


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
    phone = StringField("Phone number", validators=[DataRequired(), ValidPhoneNumber()])
    emergency_contact_name = StringField(
        "Emergency contact name",
        validators=[
            DataRequired(),
            NotWhitespace(),
            Length(min=1, max=50),
        ],
    )
    emergency_contact_phone = StringField(
        "Emergency contact phone", validators=[DataRequired(), ValidPhoneNumber()]
    )
    referral_source = CustomSelectField(
        "Referral source",
        choices=[("", "Select referral")],
        default="",
        validators=[DataRequired()],
    )
    issues = CustomSelectMultipleField(
        "Presenting issues",
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


class FilterClientsForm(CustomFlaskForm):
    name = StringField("Search by name", validators=[Optional()])
    gender = CustomSelectField(
        "Gender",
        choices=[("", "Select gender")],
        default="",
        validators=[Optional()],
    )
    min_age = IntegerField("Minimum age", validators=[Optional(), NumberRange(min=0)])
    max_age = IntegerField("Maximum age", validators=[Optional(), NumberRange(min=0)])
    occupation = CustomSelectField(
        "Occupation",
        choices=[("", "Select occupation")],
        default="",
        validators=[Optional()],
    )
    issues = CustomSelectMultipleField(
        "Issues",
        validators=[Optional()],
        coerce=int,
    )
    referral_source = CustomSelectField(
        "Referral source",
        choices=[("", "Select referral")],
        default="",
        validators=[Optional()],
    )
    submit_filter = SubmitField("Filter Clients", render_kw={"name": "filter"})
    submit_reset_filters = SubmitField(
        "Reset Filters", render_kw={"name": "reset_filters"}
    )

    def __init__(self, *args, **kwargs):
        super(FilterClientsForm, self).__init__(*args, **kwargs)
        self.gender.populate_choices(Gender)
        self.occupation.populate_choices(Occupation)
        self.issues.populate_choices(Issue)
        self.referral_source.populate_choices(ReferralSource)
        return
