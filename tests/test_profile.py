from io import BytesIO

from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage

from app import db
from app.models import User
from app.models.client import Client
from app.models.enums import Gender
from app.models.therapist import Therapist


def test_get_user_profile_fails(client: FlaskClient, logged_in_client: User):
    response = client.get("/profile/user")
    assert response.status_code == 405
    return


def test_update_user_profile_success(client: FlaskClient, logged_in_client: User):
    user_profile_data = {
        "first_name": "Test",
        "last_name": "User",
        "gender": Gender.NON_BINARY.name,
    }

    response = client.post(
        "/profile/user", data=user_profile_data, content_type="multipart/form-data"
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True and "url" in data
    updated_user = db.session.query(User).filter_by(id=logged_in_client.id).first()
    assert updated_user.first_name == user_profile_data["first_name"]
    assert updated_user.last_name == user_profile_data["last_name"]
    assert updated_user.gender.name == user_profile_data["gender"]
    return


def test_update_user_profile_missing_fields(
    client: FlaskClient, logged_in_client: User
):
    response = client.post("/profile/user", data={}, content_type="multipart/form-data")
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False and "errors" in data
    assert "first_name" in data["errors"]
    assert "last_name" in data["errors"]
    assert "gender" in data["errors"]
    return


def test_update_user_profile_invalid_file_type(
    client: FlaskClient, logged_in_client: User
):
    fake_file = FileStorage(
        stream=BytesIO(b"My fake content"),
        filename="test.txt",
        content_type="text/plain",
    )

    user_profile_data = {
        "first_name": logged_in_client.first_name,
        "last_name": logged_in_client.last_name,
        "gender": logged_in_client.gender.name,
        "profile_picture": fake_file,
    }

    response = client.post(
        "/profile/user", data=user_profile_data, content_type="multipart/form-data"
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False
    assert "profile_picture" in data["errors"]
    return


def test_get_therapist_profile_fails(client: FlaskClient):
    response = client.get("/profile/therapist")
    assert response.status_code == 405
    return


def test_update_therapist_profile_success(
    client: FlaskClient, logged_in_therapist: User, fake_therapist_profile_data: dict
):
    initial_therapist_count = db.session.execute(
        db.select(db.func.count()).select_from(Therapist)
    ).scalar()

    response = client.post("/profile/therapist", data=fake_therapist_profile_data)
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True and "url" in data
    assert (
        db.session.execute(db.select(db.func.count()).select_from(Therapist)).scalar()
        == initial_therapist_count + 1
    )
    return


def test_update_therapist_profile_missing_fields(
    client: FlaskClient, logged_in_therapist: User
):
    initial_therapist_count = db.session.execute(
        db.select(db.func.count()).select_from(Therapist)
    ).scalar()

    response = client.post("/profile/therapist", data={})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False
    assert data["success"] is False and "errors" in data
    assert (
        db.session.execute(db.select(db.func.count()).select_from(Therapist)).scalar()
        == initial_therapist_count
    )
    return


def test_get_client_profile_fails(client: FlaskClient):
    response = client.get("/profile/client")
    assert response.status_code == 405
    return


def test_update_client_profile_success(
    client: FlaskClient, logged_in_client: User, fake_client_profile_data: dict
):
    initial_client_count = db.session.execute(
        db.select(db.func.count()).select_from(Client)
    ).scalar()

    response = client.post("/profile/client", data=fake_client_profile_data)
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True and "url" in data
    assert (
        db.session.execute(db.select(db.func.count()).select_from(Client)).scalar()
        == initial_client_count + 1
    )
    return


def test_update_client_profile_missing_fields(
    client: FlaskClient,
    logged_in_client: User,
):
    initial_client_count = db.session.execute(
        db.select(db.func.count()).select_from(Client)
    ).scalar()

    response = client.post("/profile/client", data={})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True and "url" in data
    assert (
        db.session.execute(db.select(db.func.count()).select_from(Client)).scalar()
        == initial_client_count
    )
    return
