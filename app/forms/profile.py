import pycountry
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.forms import CustomSelectField, CustomSelectMultipleField
from app.models.enums import Gender
from app.models.issue import Issue
from app.models.language import Language
from app.models.session_format import SessionFormatModel
from app.utils.validators import TherapistLocationValidator, WhitespaceValidator


class TherapistProfileForm(FlaskForm):
    gender = SelectField(
        "Gender",
        choices=[(gender.name, gender.value.capitalize()) for gender in Gender],
        validators=[DataRequired()],
    )
    country = SelectField(
        "Country",
        choices=[(country.name, country.name) for country in pycountry.countries],
        validators=[DataRequired()],
    )
    languages = CustomSelectMultipleField(
        "Languages spoken",
        validators=[DataRequired()],
        coerce=int,
    )
    affiliation = StringField(
        "Affiliation", validators=[Optional(), WhitespaceValidator()]
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
    registrations = StringField(
        "Registrations", validators=[Optional(), WhitespaceValidator()]
    )
    qualifications = StringField(
        "Qualifications", validators=[Optional(), WhitespaceValidator()]
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
    preferred_gender = SelectField(
        "Preferred gender",
        choices=[(gender.name, gender.value.capitalize()) for gender in Gender],
        validators=[Optional()],
    )
    preferred_language = CustomSelectField(
        "Preferred language",
        validators=[Optional()],
        coerce=int,
    )
    session_formats = CustomSelectMultipleField(
        "Session formats",
        validators=[Optional()],
        coerce=int,
    )
    issues = CustomSelectMultipleField(
        "Specialisations",
        validators=[Optional()],
        coerce=int,
    )

    def __init__(self, *args, **kwargs):
        super(ClientProfileForm, self).__init__(*args, **kwargs)
        self.preferred_language.populate_choices(Language)
        self.issues.populate_choices(Issue)
        self.session_formats.populate_choices(SessionFormatModel)
        return
