from wtforms import SelectMultipleField

from app import db


class CustomSelectMultipleField(SelectMultipleField):
    def populate_choices_from_model(self, model) -> None:
        self.choices = [
            (row.id, row.name) for row in db.session.execute(db.select(model)).scalars()
        ]
        return

    def get_association_data(
        self, parent_id: int, parent_key: str, child_key: str
    ) -> list:
        return [{parent_key: parent_id, child_key: child_id} for child_id in self.data]
