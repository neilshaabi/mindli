from unittest.mock import Mock, patch

from flask.testing import FlaskClient

from app import db
from app.models import User


@patch('app.views.auth.login_user')
def test_get_login(mock_login_user: Mock, client: FlaskClient):
    response = client.get("/login")
    assert response.status_code == 200
    mock_login_user.assert_not_called()
    return


@patch('app.views.auth.login_user')
def test_user_login_success(mock_login_user: Mock, client: FlaskClient, fake_user_client: User, fake_user_password: str):
    response = client.post("/login", data={
        "email": fake_user_client.email,
        "password": fake_user_password,
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "url" in data and data["url"] == "/index"
    mock_login_user.assert_called_once()
    return


@patch('app.views.auth.login_user')
def test_user_login_missing_credentials(mock_login_user: Mock, client: FlaskClient):
    response = client.post("/login", data={})
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is False
    assert "errors" in data
    assert "email" in data["errors"] and "password" in data["errors"]
    mock_login_user.assert_not_called()
    return


@patch('app.views.auth.login_user')
def test_user_login_wrong_credentials(mock_login_user: Mock, client: FlaskClient, fake_user_client: User):
    response = client.post("/login", data={
        "email": fake_user_client.email,
        "password": "wrongpassword",
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is False
    assert "errors" in data
    assert "password" in data["errors"]
    mock_login_user.assert_not_called()
    return


@patch('app.views.auth.login_user')
def test_user_login_unverified(mock_login_user: Mock, client: FlaskClient, fake_user_client: User, fake_user_password: str):
    fake_user_client.verified = False
    db.session.commit()
    response = client.post("/login", data={
        "email": fake_user_client.email,
        "password": fake_user_password
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] is True
    assert "url" in data and data["url"] == "/verify-email"
    mock_login_user.assert_not_called()
    fake_user_client.verified = True
    db.session.commit()
    return
