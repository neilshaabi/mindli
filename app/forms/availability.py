from wtforms import SelectField, SubmitField, TimeField
from wtforms.validators import DataRequired

from app.forms import CustomFlaskForm

class AvailabilityForm(CustomFlaskForm):
    day_of_week = SelectField('Day of Week', choices=[
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday')
], coerce=int)
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    submit = SubmitField('Set availability')