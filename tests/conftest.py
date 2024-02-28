from datetime import date
from typing import Any, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_login import current_user
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.config import TestConfig
from app.models.enums import UserRole
from app.models.user import User


def get_csrf_token(client: FlaskClient, url: str = "/login") -> str:
    response = client.get(url)
    csrf_token = (
        response.data.decode()
        .split('name="csrf_token" type="hidden" value="')[1]
        .split('"')[0]
    )
    return csrf_token


def post_with_csrf(client: FlaskClient, url: str, data: dict):
    csrf_token = get_csrf_token(client)
    data["csrf_token"] = csrf_token
    return client.post(url, data=data, follow_redirects=True)


@pytest.fixture(scope="function")
def app() -> Generator[Flask, Any, None]:
    app = create_app(config=TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()
    return


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope="function")
def fake_user_password() -> str:
    return "ValidPassword1"


@pytest.fixture(scope="function")
def fake_user_client(fake_user_password: str) -> Generator[User, Any, None]:
    fake_user_client = User(
        email="client@example.com".lower(),
        password_hash=generate_password_hash(fake_user_password),
        first_name="John",
        last_name="Smith",
        date_joined=date.today(),
        role=UserRole.CLIENT,
        verified=True,
        active=True,
    )
    db.session.add(fake_user_client)
    db.session.commit()

    yield fake_user_client

    db.session.delete(fake_user_client)
    db.session.commit()
    return


@pytest.fixture(scope="function")
def new_user_data(fake_user_client: User, fake_user_password: str) -> dict:
    return {
        "role": fake_user_client.role.value,
        "first_name": fake_user_client.first_name,
        "last_name": fake_user_client.last_name,
        "email": "different-" + fake_user_client.email,
        "password": fake_user_password,
    }


@pytest.fixture(scope="function")
def fake_user_therapist(fake_user_password: str) -> Generator[User, Any, None]:
    fake_user_therapist = User(
        email="therapist@example.com".lower(),
        password_hash=generate_password_hash(fake_user_password),
        first_name="Alice",
        last_name="Gray",
        date_joined=date.today(),
        role=UserRole.THERAPIST,
        verified=True,
        active=True,
    )
    db.session.add(fake_user_therapist)
    db.session.commit()

    yield fake_user_therapist

    db.session.delete(fake_user_therapist)
    db.session.commit()
    return


@pytest.fixture(scope="function")
def logged_in_therapist(
    client: FlaskClient, fake_user_therapist: User, fake_user_password: str
) -> Generator[User, Any, None]:
    with client:
        response = post_with_csrf(
            client=client,
            url="/login",
            data={
                "email": fake_user_therapist.email,
                "password": fake_user_password,
            },
        )
        assert response.status_code == 200
        assert current_user.is_authenticated

        yield fake_user_therapist

        client.get("/logout")
        return
