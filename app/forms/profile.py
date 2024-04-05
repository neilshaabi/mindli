import pycountry
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.forms import CustomSelectField, CustomSelectMultipleField
from app.models.enums import Gender
from app.models.issue import Issue
from app.models.language import Language
from app.models.session_format import SessionFormatModel
from app.utils.validators import TherapistLocationValidator, WhitespaceValidator


class UserProfileForm(FlaskForm):
    profile_picture = FileField(
        "Profile picture",
        validators=[FileAllowed(["jpg", "png"], "Uploaded file must be in jpg or png format.")],
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
        + [(gender.name, gender.value.capitalize()) for gender in Gender],
        validators=[DataRequired()],
        default="",
    )


class TherapistProfileForm(FlaskForm):
    country = SelectField(
        "Country",
        choices=[("", "Select country")]
        + [(country.name, country.name) for country in pycountry.countries],
        validators=[DataRequired()],
        default="",
    )
    languages = CustomSelectMultipleField(
        "Languages spoken",
        validators=[DataRequired()],
        coerce=int,
    )
    bio = TextAreaField("Bio", validators=[Optional(), WhitespaceValidator()])
    link = StringField(
        "Link", validators=[Optional(), WhitespaceValidator(), Length(max=255)]
    )
    location = StringField(
        "Location",
        validators=[
            WhitespaceValidator(),
            Length(max=255),
            TherapistLocationValidator(),
        ],
    )
    years_of_experience = IntegerField(
        "Years of experience", validators=[Optional(), NumberRange(min=0)]
    )
    qualifications = StringField(
        "Qualifications", validators=[Optional(), WhitespaceValidator()]
    )
    registrations = StringField(
        "Registrations", validators=[Optional(), WhitespaceValidator()]
    )
    session_formats = CustomSelectMultipleField(
        "Session formats",
        validators=[DataRequired()],
        coerce=int,
    )
    issues = CustomSelectMultipleField(
        "Specialisations",
        validators=[DataRequired()],
        coerce=int,
    )

    def __init__(self, *args, **kwargs):
        super(TherapistProfileForm, self).__init__(*args, **kwargs)
        self.languages.populate_choices(Language)
        self.issues.populate_choices(Issue)
        self.session_formats.populate_choices(SessionFormatModel)
        return


class ClientProfileForm(FlaskForm):
    preferred_gender = CustomSelectField(
        "Preferred gender",
        choices=[("", "Select gender")]
        + [(gender.name, gender.value.capitalize()) for gender in Gender],
        validators=[Optional()],
    )
    preferred_language = CustomSelectField(
        "Preferred language",
        choices=[(0, "Select language")],
        validators=[Optional()],
        coerce=int,
    )
    session_formats = CustomSelectMultipleField(
        "Session formats",
        validators=[Optional()],
        coerce=int,
    )
    issues = CustomSelectMultipleField(
        "Issues",
        validators=[Optional()],
        coerce=int,
    )

    def __init__(self, *args, **kwargs):
        super(ClientProfileForm, self).__init__(*args, **kwargs)
        self.preferred_language.populate_choices(Language)
        self.issues.populate_choices(Issue)
        self.session_formats.populate_choices(SessionFormatModel)
        return
