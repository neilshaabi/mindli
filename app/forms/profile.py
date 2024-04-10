import pycountry
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.forms import CustomFlaskForm, CustomSelectField, CustomSelectMultipleField
from app.models.enums import Gender
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.title import Title
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


class TherapistProfileForm(CustomFlaskForm):
    titles = CustomSelectMultipleField(
        "Professional titles",
        validators=[DataRequired()],
        coerce=int,
    )
    years_of_experience = IntegerField(
        "Years of experience", validators=[DataRequired(), NumberRange(min=0)]
    )
    qualifications = StringField(
        "Qualifications", validators=[DataRequired(), NotWhitespace()]
    )
    registrations = StringField(
        "Registrations", validators=[Optional(), NotWhitespace()]
    )
    country = SelectField(
        "Country",
        choices=[("", "Select country")]
        + [(country.name, country.name) for country in pycountry.countries],
        default="",
        validators=[DataRequired()],
    )
    location = StringField(
        "Location (in-person appointments)",
        validators=[
            NotWhitespace(),
            Length(max=255),
        ],
    )
    languages = CustomSelectMultipleField(
        "Languages spoken",
        validators=[DataRequired()],
        coerce=int,
    )
    issues = CustomSelectMultipleField(
        "Specialisations",
        validators=[DataRequired()],
        coerce=int,
    )
    interventions = CustomSelectMultipleField(
        "Interventions",
        validators=[DataRequired()],
        coerce=int,
    )
    link = StringField(
        "Professional website",
        validators=[Optional(), NotWhitespace(), Length(max=255)],
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(TherapistProfileForm, self).__init__(*args, **kwargs)

        self.titles.populate_choices(Title)
        self.languages.populate_choices(Language)
        self.issues.populate_choices(Issue)
        self.interventions.populate_choices(Intervention)

        therapist = kwargs.get("obj")
        if therapist:
            self.titles.preselect_choices(therapist.titles)
            self.languages.preselect_choices(therapist.languages)
            self.issues.preselect_choices(therapist.specialisations)
            self.interventions.preselect_choices(therapist.interventions)
        return


class ClientProfileForm(CustomFlaskForm):
    date_of_birth = DateField(
        "Date of birth",
        validators=[DataRequired()],
    )
    occupation = SelectField(
        "Occupation",
        choices=[
            ("", "Select occupation"),
            ("healthcare", "Healthcare"),
            ("education", "Education"),
            ("it", "IT/Technology"),
            ("finance", "Finance"),
            ("arts", "Arts & entertainment"),
            ("student", "Student"),
            ("unemployed", "Unemployed"),
            ("other", "Other"),
        ],
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
        choices=[
            ("", "Select referral source"),
            ("mindli", "Mindli"),
            ("internet", "Internet"),
            ("friend_family", "Friend/family"),
            ("healthcare_provider", "Healthcare provider"),
            ("social_media", "Social media"),
            ("other", "Other"),
        ],
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
