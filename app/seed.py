from flask_sqlalchemy import SQLAlchemy

from app.models import SeedableMixin


def seed_db(db: SQLAlchemy) -> None:
    for model in SeedableMixin.__subclasses__():
        model.seed(db)
    return
