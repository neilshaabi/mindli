from unittest.mock import Mock, patch

import pytest
from flask.testing import FlaskClient
from flask_mail import Mail

from app import db
from app.models import User


@pytest.fixture(scope="function")
def new_user_data(fake_user_client: User, fake_user_password: str) -> dict:
    return {
        "role": fake_user_client.role.value,
        "first_name": fake_user_client.first_name,
        "last_name": fake_user_client.last_name,
        "email": "different-" + fake_user_client.email,
        "password": fake_user_password,
    }


def test_get_register(client: FlaskClient):
    response = client.get("/register")
    assert response.status_code == 200
    return


@patch.object(Mail, "send")
def test_register_success(
    mock_send_email: Mock, client: FlaskClient, new_user_data: dict
):
    response = client.post("/register", data=new_user_data)
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert "url" in data
    assert (
        db.session.execute(
            db.select(User).filter_by(email=new_user_data["email"].lower())
        ).scalar_one_or_none()
        is not None
    )
    mock_send_email.assert_called_once()

    return


@patch.object(Mail, "send")
def test_register_missing_fields(mock_send_email: Mock, client: FlaskClient):
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response = client.post("/register", data={})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False
    assert "errors" in data
    assert (
        db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
        == initial_user_count
    )
    mock_send_email.assert_not_called()

    return


@patch.object(Mail, "send")
def test_register_invalid_role(
    mock_send_email: Mock, client: FlaskClient, new_user_data: dict
):
    invalid_user_data = new_user_data.copy()
    invalid_user_data["role"] = "invalid_role"
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response = client.post("/register", data=invalid_user_data)
    data = response.get_json()

    assert response.status_code == 200
    assert "errors" in data
    assert "role" in data["errors"]
    assert (
        db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
        == initial_user_count
    )
    mock_send_email.assert_not_called()

    return


@patch.object(Mail, "send")
def test_register_invalid_email(
    mock_send_email: Mock, client: FlaskClient, new_user_data: dict
):
    invalid_user_data = new_user_data.copy()
    invalid_user_data["email"] = "invalidemail"
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response = client.post("/register", data=invalid_user_data)
    data = response.get_json()

    assert response.status_code == 200
    assert "errors" in data
    assert "email" in data["errors"]
    assert (
        db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
        == initial_user_count
    )
    mock_send_email.assert_not_called()

    return


@patch.object(Mail, "send")
def test_register_duplicate_email(
    mock_send_email: Mock, client: FlaskClient, new_user_data: dict
):
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response = client.post("/register", data=new_user_data)
    data = response.get_json()

    assert response.status_code == 200
    assert "errors" in data
    assert "email" in data["errors"]
    assert (
        db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
        == initial_user_count
    )
    mock_send_email.assert_not_called()

    return


@patch.object(Mail, "send")
def test_register_weak_password(
    mock_send_email: Mock, client: FlaskClient, new_user_data: dict
):
    invalid_user_data = new_user_data.copy()
    invalid_user_data["password"] = "123"
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response = client.post("/register", data=invalid_user_data)
    data = response.get_json()

    assert response.status_code == 200
    assert "errors" in data
    assert "password" in data["errors"]
    assert (
        db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
        == initial_user_count
    )
    mock_send_email.assert_not_called()

    return
