from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired

from app.forms import CustomFlaskForm
from app.utils.validators import NotWhitespace


class SendMessageForm(CustomFlaskForm):
    conversation_id = HiddenField()
    message = StringField(
        "Type a message", validators=[DataRequired(), NotWhitespace()]
    )
    submit = SubmitField("Send")
