from typing import List, Type

from flask_sqlalchemy.model import Model
from wtforms import SelectField, SelectMultipleField

from app import db


class SelectFieldMixin:
    def populate_choices(self, model: Type[Model]) -> None:
        self.choices = [
            (row.id, row.name) for row in db.session.execute(db.select(model)).scalars()
        ]
        return

    def preselect_choices(self, data: List[Model]) -> None:
        self.data = [row.id for row in data]
        return

    def update_association_data(
        self,
        parent: Model,
        child: Type[Model],
        children: str,
    ) -> None:
        getattr(parent, children).clear()

        if self.data is None:
            return

        selected_data = db.session.execute(
            db.select(child).filter(child.id.in_(self.data))
        ).scalars()
        getattr(parent, children).extend(selected_data)
        return


class CustomSelectField(SelectFieldMixin, SelectField):
    pass


class CustomSelectMultipleField(SelectFieldMixin, SelectMultipleField):
    pass
