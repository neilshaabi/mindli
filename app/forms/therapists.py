import pycountry
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import Optional

from app.forms import CustomFlaskForm, CustomSelectField, CustomSelectMultipleField
from app.models.enums import Gender, TherapyMode, TherapyType
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.title import Title


class FilterTherapistsForm(CustomFlaskForm):
    therapy_type = CustomSelectField(
        "Therapy type",
        choices=[("", "Select type")],
        validators=[Optional()],
    )
    therapy_mode = CustomSelectMultipleField(
        "Mode",
        validators=[Optional()],
    )
    duration = IntegerField("Duration", validators=[Optional()])
    titles = CustomSelectMultipleField(
        "Titles",
        validators=[Optional()],
        coerce=int,
    )
    years_of_experience = IntegerField(
        "Minimum years of experience", validators=[Optional()], default=0
    )
    gender = CustomSelectField(
        "Gender",
        choices=[("", "Select gender")],
        default="",
        validators=[Optional()],
    )
    language = CustomSelectField(
        "Language",
        choices=[(0, "Select language")],
        validators=[Optional()],
        coerce=int,
    )
    country = SelectField(
        "Country",
        choices=[("", "Select country")]
        + [(country.name, country.name) for country in pycountry.countries],
        default="",
        validators=[Optional()],
    )
    specialisations = CustomSelectMultipleField(
        "Specialisations",
        validators=[Optional()],
        coerce=int,
    )
    interventions = CustomSelectMultipleField(
        "Interventions",
        validators=[Optional()],
        coerce=int,
    )
    submit = SubmitField("Filter")

    def __init__(self, *args, **kwargs):
        super(FilterTherapistsForm, self).__init__(*args, **kwargs)
        self.therapy_type.populate_choices(TherapyType)
        self.therapy_mode.populate_choices(TherapyMode)
        self.titles.populate_choices(Title)
        self.gender.populate_choices(Gender)
        self.language.populate_choices(Language)
        self.specialisations.populate_choices(Issue)
        self.interventions.populate_choices(Intervention)

        #     client = kwargs.get("obj")
        #     if client:
        #         self.preferred_language.preselect_choices(client.preferred_language)
        #         self.preferred_gender.preselect_choices(client.preferred_gender)
        #         self.issues.preselect_choices(client.issues)
        return
