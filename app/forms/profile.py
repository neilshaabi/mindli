import pycountry
from flask_wtf.file import FileAllowed, FileField
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.forms import CustomFlaskForm, CustomSelectField, CustomSelectMultipleField
from app.models.enums import Gender
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.title import Title
from app.utils.validators import WhitespaceValidator


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
        choices=[("", "Select gender")]
        + [(gender.name, gender.value) for gender in Gender],
        validators=[DataRequired()],
        default="",
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
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
        "Qualifications", validators=[DataRequired(), WhitespaceValidator()]
    )
    registrations = StringField(
        "Registrations", validators=[Optional(), WhitespaceValidator()]
    )
    country = SelectField(
        "Country",
        choices=[("", "Select country")]
        + [(country.name, country.name) for country in pycountry.countries],
        validators=[DataRequired()],
        default="",
    )
    location = StringField(
        "Location (in-person appointments)",
        validators=[
            WhitespaceValidator(),
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
        validators=[Optional(), WhitespaceValidator(), Length(max=255)],
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
    preferred_gender = CustomSelectField(
        "Preferred gender",
        choices=[("", "Select gender")]
        + [(gender.name, gender.value) for gender in Gender],
        validators=[Optional()],
    )
    preferred_language = CustomSelectField(
        "Preferred language",
        choices=[(0, "Select language")],
        validators=[Optional()],
        coerce=int,
    )
    issues = CustomSelectMultipleField(
        "Issues",
        validators=[Optional()],
        coerce=int,
    )
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(ClientProfileForm, self).__init__(*args, **kwargs)

        self.preferred_language.populate_choices(Language)
        self.issues.populate_choices(Issue)

        client = kwargs.get("obj")
        if client:
            self.preferred_language.preselect_choices(client.preferred_language)
            self.preferred_gender.preselect_choices(client.preferred_gender)
            self.issues.preselect_choices(client.issues)
        return
