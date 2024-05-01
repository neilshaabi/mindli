from wtforms import SubmitField, TextAreaField
from wtforms.validators import Optional

from app.forms import CustomFlaskForm, CustomSelectMultipleField
from app.models.intervention import Intervention
from app.models.issue import Issue


class TreatmentPlanForm(CustomFlaskForm):
    issues = CustomSelectMultipleField(
        "Presenting issues",
        validators=[Optional()],
        coerce=int,
    )
    issues_description = TextAreaField(
        "Description of presenting issues", validators=[Optional()]
    )
    interventions = CustomSelectMultipleField(
        "Interventions",
        validators=[Optional()],
        coerce=int,
    )
    interventions_description = TextAreaField(
        "Description of interventions", validators=[Optional()]
    )
    goals = TextAreaField("Treatment goals", validators=[Optional()])
    medication = TextAreaField("Medication", validators=[Optional()])

    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(TreatmentPlanForm, self).__init__(*args, **kwargs)

        self.issues.populate_choices(Issue)
        self.interventions.populate_choices(Intervention)

        plan = kwargs.get("obj")
        if plan:
            self.issues.preselect_choices(plan.issues)
            self.interventions.preselect_choices(plan.interventions)
        return
