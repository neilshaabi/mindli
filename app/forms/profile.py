from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DateField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length

from app.constants import OCCUPATIONS, REFERRAL_SOURCES
from app.forms import CustomFlaskForm, CustomSelectField, CustomSelectMultipleField
from app.models.enums import Gender
from app.models.issue import Issue
from app.utils.validators import NotWhitespace, ValidPhoneNumber


class UserProfileForm(CustomFlaskForm):
    profile_picture = FileField(
        "Profile picture",
        validators=[
            FileAllowed(["jpg", "png"], "Uploaded file must be in jpg or png format.")
        ],
    )
    first_name = StringField(
        "First name", validators=[DataRequired(), Length(min=1, max=50)]
    )
    last_name = StringField(
        "Last name", validators=[DataRequired(), Length(min=1, max=50)]
    )
    gender = CustomSelectField(
        "Gender",
        choices=[("", "Select gender")],
        default="",
        validators=[DataRequired()],
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.gender.populate_choices(Gender)
        user = kwargs.get("obj")
        if user:
            self.gender.preselect_choices(user.gender)
        return


class ClientProfileForm(CustomFlaskForm):
    date_of_birth = DateField(
        "Date of birth",
        validators=[DataRequired()],
    )
    occupation = SelectField(
        "Occupation",
        choices=[("", "Select occupation")] + OCCUPATIONS,
        default="",
        validators=[DataRequired()],
    )
    address = StringField(
        "Address", validators=[DataRequired(), NotWhitespace(), Length(max=255)]
    )
    phone = StringField("Phone Number", validators=[DataRequired(), ValidPhoneNumber()])
    emergency_contact_name = StringField(
        "Emergency contact name",
        validators=[DataRequired(), NotWhitespace(), Length(max=100)],
    )
    emergency_contact_phone = StringField(
        "Emergency contact phone", validators=[DataRequired(), ValidPhoneNumber()]
    )
    referral_source = SelectField(
        "Referral source",
        choices=[("", "Select referral source")] + REFERRAL_SOURCES,
        default="",
        validators=[DataRequired(), Length(max=100)],
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

        self.issues.populate_choices(Issue)

        client = kwargs.get("obj")
        if client:
            self.issues.preselect_choices(client.issues)
        return
