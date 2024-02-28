import click
import pycountry
from flask import Flask

from app import db
from app.models import Language


def register_cli_commands(app: Flask):
    @app.cli.command("seed-db")
    def seed_db() -> None:
        seed_languages()
        click.echo("Seeding database with languages...")
        return

    return


def seed_languages() -> None:
    languages = []
    for language in pycountry.languages:
        if language.type == "L":  # Only include 'living' languages
            languages.append(
                Language(
                    name=language.name,
                    alpha_2=getattr(language, "alpha_2", None),
                    alpha_3=getattr(language, "alpha_3", None),
                )
            )
    db.session.add_all(languages)
    db.session.commit()
    return
