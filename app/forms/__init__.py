from wtforms import SelectField, SelectMultipleField

from app import db


class SelectFieldMixin:
    def populate_choices_from_model(self, model) -> None:
        self.choices = [
            (row.id, row.name) for row in db.session.execute(db.select(model)).scalars()
        ]
        return

    def get_association_data(
        self, parent_id: int, parent_key: str, child_key: str
    ) -> list:
        child_ids = self.data if isinstance(self.data, list) else [self.data]
        return [{parent_key: parent_id, child_key: child_id} for child_id in child_ids]


class CustomSelectField(SelectFieldMixin, SelectField):
    pass


class CustomSelectMultipleField(SelectFieldMixin, SelectMultipleField):
    pass
