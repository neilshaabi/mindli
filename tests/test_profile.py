from flask.testing import FlaskClient

from app import db
from app.models import User
from app.models.therapist import Therapist


def test_get_therapist_profile_unauthenticated(client: FlaskClient):
    response = client.get("/therapist/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    return


def test_get_therapist_profile_as_client(client: FlaskClient, logged_in_client: User):
    response = client.get("/therapist/profile")
    assert response.status_code == 302
    return


def test_get_therapist_profile_success(client: FlaskClient, logged_in_therapist: User):
    response = client.get("/therapist/profile")
    assert response.status_code == 200
    return


def test_update_therapist_profile_success(
    client: FlaskClient, logged_in_therapist: User, therapist_profile_data: dict
):
    initial_therapist_count = db.session.execute(
        db.select(db.func.count()).select_from(Therapist)
    ).scalar()

    response = client.post("/therapist/profile", data=therapist_profile_data)
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert "url" in data
    assert (
        db.session.execute(db.select(db.func.count()).select_from(Therapist)).scalar()
        == initial_therapist_count + 1
    )
    return


def test_update_therapist_profile_missing_fields(
    client: FlaskClient, logged_in_therapist: User, therapist_profile_data: dict
):
    initial_therapist_count = db.session.execute(
        db.select(db.func.count()).select_from(Therapist)
    ).scalar()

    response = client.post("/therapist/profile", data={})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False
    assert data["success"] is False and "errors" in data
    assert (
        db.session.execute(db.select(db.func.count()).select_from(Therapist)).scalar()
        == initial_therapist_count
    )
    return


def test_update_therapist_profile_without_location_fails(
    client: FlaskClient, logged_in_therapist: User, therapist_profile_data: dict
):
    initial_therapist_count = db.session.execute(
        db.select(db.func.count()).select_from(Therapist)
    ).scalar()

    invalid_therapist_data = therapist_profile_data.copy()
    invalid_therapist_data["location"] = None
    invalid_therapist_data["country"] = "test country"

    response = client.post("/therapist/profile", data=invalid_therapist_data)
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False and "errors" in data
    assert "location" in data["errors"]
    assert (
        db.session.execute(db.select(db.func.count()).select_from(Therapist)).scalar()
        == initial_therapist_count
    )
    return


def test_update_therapist_profile_without_location_success(
    client: FlaskClient, logged_in_therapist: User, therapist_profile_data: dict
):
    valid_therapist_data = therapist_profile_data.copy()
    valid_therapist_data["location"] = None
    valid_therapist_data["session_formats"] = [2]

    response = client.post("/therapist/profile", data=valid_therapist_data)
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert "url" in data
    return
