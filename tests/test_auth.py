from unittest.mock import Mock, patch

from flask.testing import FlaskClient
from flask_login import current_user
from flask_mail import Mail

from app import db
from app.models.user import User


@patch.object(Mail, "send")
def test_get_register(mock_send_email: Mock, client: FlaskClient):
    response = client.get("/register")
    assert response.status_code == 200
    mock_send_email.assert_not_called()
    return


@patch.object(Mail, "send")
def test_register_success(
    mock_send_email: Mock, client: FlaskClient, fake_registration_data: dict
):
    with client:
        response = client.post("/register", data=fake_registration_data)
        data = response.get_json()

        assert response.status_code == 200

        assert data["success"] is True

        assert "url" in data
        assert (
            db.session.execute(
                db.select(User).filter_by(email=fake_registration_data["email"].lower())
            ).scalar_one_or_none()
            is not None
        )
        mock_send_email.assert_called_once()
        assert not current_user.is_authenticated
    return


@patch.object(Mail, "send")
def test_register_missing_fields(
    mock_send_email: Mock, client: FlaskClient, fake_registration_data: dict
):
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response = client.post("/register", data={}, follow_redirects=True)
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False
    assert "errors" in data
    assert set(data["errors"]) == set(fake_registration_data.keys())
    assert (
        db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
        == initial_user_count
    )
    mock_send_email.assert_not_called()

    return


@patch.object(Mail, "send")
def test_register_invalid_role(
    mock_send_email: Mock, client: FlaskClient, fake_registration_data: dict
):
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    invalid_user_data = fake_registration_data.copy()
    invalid_user_data["role"] = "invalid_role"

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
    mock_send_email: Mock, client: FlaskClient, fake_registration_data: dict
):
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    invalid_user_data = fake_registration_data.copy()
    invalid_user_data["email"] = "invalidemail"

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
    mock_send_email: Mock, client: FlaskClient, fake_registration_data: dict
):
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response = client.post("/register", data=fake_registration_data)
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
    mock_send_email: Mock, client: FlaskClient, fake_registration_data: dict
):
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    invalid_user_data = fake_registration_data.copy()
    invalid_user_data["password"] = "123"

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


def test_get_login(client: FlaskClient):
    with client:
        response = client.get("/login")
        assert response.status_code == 200
        assert not current_user.is_authenticated
    return


def test_user_login_success(
    client: FlaskClient,
    fake_user_client: User,
    fake_user_password: str,
):
    with client:
        response = client.post(
            "/login",
            data={
                "email": fake_user_client.email,
                "password": fake_user_password,
            },
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is True
        assert "url" in data and data["url"] == "/index"
        assert current_user.is_authenticated
        client.get("/logout")
    return


def test_user_login_missing_fields(client: FlaskClient):
    with client:
        response = client.post("/login", data={})
        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is False
        assert "errors" in data
        assert set(data["errors"]) == set(["email", "password"])
        assert not current_user.is_authenticated
    return


def test_user_login_wrong_credentials(client: FlaskClient, fake_user_client: User):
    with client:
        response = client.post(
            "/login",
            data={
                "email": fake_user_client.email,
                "password": "wrongpassword",
            },
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is False
        assert "errors" in data
        assert "password" in data["errors"]
        assert not current_user.is_authenticated
    return


def test_user_login_unverified(
    client: FlaskClient,
    fake_user_client: User,
    fake_user_password: str,
):
    fake_user_client.verified = False
    db.session.commit()

    with client:
        response = client.post(
            "/login",
            data={"email": fake_user_client.email, "password": fake_user_password},
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is True
        assert "url" in data and data["url"] == "/verify-email"
        assert not current_user.is_authenticated

    fake_user_client.verified = True
    db.session.commit()
    return


@patch.object(Mail, "send")
def test_verify_email_sent(
    mock_send_email: Mock, client: FlaskClient, fake_registration_data: dict
):
    new_user_data = fake_registration_data.copy()
    new_user_data["email"] = f"new-{fake_registration_data['email']}"

    response = client.post("/register", data=new_user_data)
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "url" in data and data["url"] == "/verify-email"
    mock_send_email.assert_called_once()

    response = client.post("/verify-email", data={})
    assert response.status_code == 200
    assert mock_send_email.call_count == 2

    return
