import pycountry
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.models.enums import Gender
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
    languages = SelectMultipleField(
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

    session_formats = SelectMultipleField(
        "Session formats",
        validators=[DataRequired()],
        coerce=int,
    )

    issues = SelectMultipleField(
        "Specialisations",
        validators=[DataRequired()],
        coerce=int,
    )
