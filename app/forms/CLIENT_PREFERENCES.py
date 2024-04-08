from wtforms import SubmitField
from wtforms.validators import Optional

from app.forms import (CustomFlaskForm, CustomSelectField,
                       CustomSelectMultipleField)
from app.models.enums import Gender
from app.models.issue import Issue
from app.models.language import Language


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
