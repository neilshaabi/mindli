from flask.testing import FlaskClient
from flask_login import current_user

from app import db
from app.models import User


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


def test_user_login_missing_credentials(client: FlaskClient):
    with client:
        response = client.post("/login", data={})
        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is False
        assert "errors" in data
        assert "email" in data["errors"] and "password" in data["errors"]
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
