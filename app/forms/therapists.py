from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import Optional

from app.constants import COUNTRIES
from app.forms import (CustomFlaskForm, CustomSelectField,
                       CustomSelectMultipleField)
from app.models.enums import Gender, TherapyMode, TherapyType
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.title import Title


class FilterTherapistsForm(CustomFlaskForm):
    name = StringField("Search by name", validators=[Optional()])
    therapy_type = CustomSelectField(
        "Therapy type",
        choices=[("", "Select type")],
        validators=[Optional()],
    )
    therapy_mode = CustomSelectMultipleField(
        "Mode",
        validators=[Optional()],
    )
    duration = IntegerField("Duration (mins)", validators=[Optional()])
    titles = CustomSelectMultipleField(
        "Titles",
        validators=[Optional()],
        coerce=int,
    )
    years_of_experience = IntegerField(
        "Min. years of experience", validators=[Optional()], default=0
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
        "Based in",
        choices=[("", "Select country")]
        + [(country, country) for country in COUNTRIES],
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
    submit_filter = SubmitField("Filter Therapists", render_kw={"name": "filter"})
    submit_reset_filters = SubmitField(
        "Reset Filters", render_kw={"name": "reset_filters"}
    )

    def __init__(self, *args, **kwargs):
        super(FilterTherapistsForm, self).__init__(*args, **kwargs)
        self.therapy_type.populate_choices(TherapyType)
        self.therapy_mode.populate_choices(TherapyMode)
        self.titles.populate_choices(Title)
        self.gender.populate_choices(Gender)
        self.language.populate_choices(Language)
        self.specialisations.populate_choices(Issue)
        self.interventions.populate_choices(Intervention)
        return
