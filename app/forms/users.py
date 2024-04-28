from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.forms import CustomFlaskForm, CustomSelectField
from app.models.enums import Gender
from app.utils.validators import NotWhitespace, ValidName


class UserProfileForm(CustomFlaskForm):
    profile_picture = FileField(
        "Profile picture",
        validators=[
            FileAllowed(["jpg", "png"], "Uploaded file must be in jpg or png format.")
        ],
    )
    first_name = StringField(
        "First name",
        validators=[
            DataRequired(),
            NotWhitespace(),
            ValidName(),
            Length(min=1, max=50),
        ],
    )
    last_name = StringField(
        "Last name",
        validators=[
            DataRequired(),
            NotWhitespace(),
            ValidName(),
            Length(min=1, max=50),
        ],
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
