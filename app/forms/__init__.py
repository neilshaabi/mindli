from wtforms import SelectMultipleField
from app import db


class CustomSelectMultipleField(SelectMultipleField):
    def populate_choices_from_model(self, model) -> None:
        self.choices = [
        (row.id, row.name)
        for row in db.session.execute(db.select(model)).scalars()
    ]