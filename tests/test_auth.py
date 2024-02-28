from unittest.mock import Mock, patch

from flask.testing import FlaskClient
from flask_login import current_user
from flask_mail import Mail

from app import db
from app.models.user import User
from tests.conftest import post_with_csrf


@patch.object(Mail, "send")
def test_get_register(mock_send_email: Mock, client: FlaskClient):
    response = client.get("/register")
    assert response.status_code == 200
    mock_send_email.assert_not_called()
    return


@patch.object(Mail, "send")
def test_register_success(
    mock_send_email: Mock, client: FlaskClient, new_user_data: dict
):
    with client:
        response = post_with_csrf(client=client, url="/register", data=new_user_data)
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
        assert not current_user.is_authenticated
    return


@patch.object(Mail, "send")
def test_register_missing_fields(mock_send_email: Mock, client: FlaskClient):
    initial_user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response = post_with_csrf(client=client, url="/register", data={})
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

    response = post_with_csrf(client=client, url="/register", data=invalid_user_data)
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

    response = post_with_csrf(client=client, url="/register", data=invalid_user_data)
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
    response_1 = post_with_csrf(client=client, url="/register", data=new_user_data)
    data_1 = response_1.get_json()
    assert response_1.status_code == 200
    assert data_1["success"] is True

    user_count = db.session.execute(
        db.select(db.func.count()).select_from(User)
    ).scalar()

    response_2 = post_with_csrf(client=client, url="/register", data=new_user_data)
    data_2 = response_2.get_json()

    assert response_2.status_code == 200
    assert "errors" in data_2
    assert "email" in data_2["errors"]
    assert (
        db.session.execute(db.select(db.func.count()).select_from(User)).scalar()
        == user_count
    )
    mock_send_email.assert_called_once()

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

    response = post_with_csrf(client=client, url="/register", data=invalid_user_data)
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
        response = post_with_csrf(
            client=client,
            url="/login",
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


def test_user_login_missing_credentials(client: FlaskClient):
    with client:
        response = post_with_csrf(client=client, url="/login", data={})
        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is False
        assert "errors" in data
        assert "email" in data["errors"] and "password" in data["errors"]
        assert not current_user.is_authenticated
    return


def test_user_login_wrong_credentials(client: FlaskClient, fake_user_client: User):
    with client:
        response = post_with_csrf(
            client=client,
            url="/login",
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
        response = post_with_csrf(
            client=client,
            url="/login",
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
def test_verify_email_sent(mock_send_email: Mock, client: FlaskClient, new_user_data):
    # Register user
    response = post_with_csrf(client=client, url="/register", data=new_user_data)
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "url" in data and data["url"] == "/verify-email"
    mock_send_email.assert_called_once()

    # Trigger the verify_email route
    response = post_with_csrf(client=client, url="/verify-email", data={})
    assert response.status_code == 200
    assert mock_send_email.call_count == 2

    return
