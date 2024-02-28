import pycountry
from flask import Flask

from app import db
from app.models.enums import SessionFormat
from app.models.issue import Issue
from app.models.language import Language
from app.models.session_format import SessionFormatModel


def register_cli_commands(app: Flask):
    @app.cli.command("seed-db")
    def seed_db_cli() -> None:
        seed_db()
        return

    return


def seed_db() -> None:
    seed_languages()
    seed_session_formats()
    seed_issues()
    return


def seed_languages() -> None:
    languages = [
        Language(
            name=language.name,
            alpha_2=getattr(language, "alpha_2", None),
            alpha_3=getattr(language, "alpha_3", None),
        )
        for language in pycountry.languages
        if language.type == "L"
    ]
    db.session.add_all(languages)
    db.session.commit()
    return


def seed_session_formats() -> None:
    session_formats = [
        SessionFormatModel(name=session_format.value)
        for session_format in SessionFormat
    ]
    db.session.add_all(session_formats)
    db.session.commit()
    return


def seed_issues():
    issue_names = [
        "Anxiety",
        "Depression",
        "Stress",
        # Add more based on your research
    ]
    issues = [Issue(name=issue_name) for issue_name in issue_names]
    db.session.add_all(issues)
    db.session.commit()
    return
