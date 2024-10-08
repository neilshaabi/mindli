from enum import Enum
from typing import List, Type, Union

from flask import session
from flask_sqlalchemy.model import Model
from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField

from app import db


class CustomFlaskForm(FlaskForm):
    def __init__(self, id=None, endpoint=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.id = id
        self.endpoint = endpoint

    def store_data_in_session(self, session_key: str) -> None:
        session[session_key] = {}
        for field_name, field in self._fields.items():
            if field_name != "csrf_token":
                session[session_key][field_name] = field.data


class SelectFieldMixin:
    def populate_choices(self, source: Union[Type[Model], Enum]) -> None:
        if issubclass(source, Enum):
            choices = [(member.name, member.value) for member in source]
        else:
            choices = [
                (row.id, row.name)
                for row in db.session.execute(db.select(source)).scalars().all()
            ]
        if self.choices is None:
            self.choices = choices
        else:
            self.choices.extend(choices)
        return

    def preselect_choices(self, data) -> None:
        pass

    def update_association_data(
        self,
        parent: Model,
        child: Type[Model],
        children: str,
    ) -> None:
        getattr(parent, children).clear()

        if self.data is None:
            return

        selected_data = (
            db.session.execute(db.select(child).filter(child.id.in_(self.data)))
            .scalars()
            .all()
        )
        getattr(parent, children).extend(selected_data)
        return


class CustomSelectField(SelectFieldMixin, SelectField):
    def preselect_choices(self, data: Union[Model, Enum]) -> None:
        if data is not None:
            self.data = data.name if isinstance(data, Enum) else data.id
        return


class CustomSelectMultipleField(SelectFieldMixin, SelectMultipleField):
    def preselect_choices(self, data: List[Model]) -> None:
        self.data = [row.id for row in data]
        return
