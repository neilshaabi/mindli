import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app, db
from app.config import TestConfig


@pytest.fixture()
def app():
    app = create_app(config=TestConfig)

    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()
