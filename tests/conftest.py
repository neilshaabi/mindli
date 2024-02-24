from typing import Any, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import TestConfig


@pytest.fixture()
def app() -> Generator[Flask, Any, None]:
    app = create_app(config=TestConfig)
    yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()
