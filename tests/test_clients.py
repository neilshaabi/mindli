from app import db
from flask.testing import FlaskClient

from app.models import User
from app.models.client import Client
from app.models.therapist import Therapist


def test_get_clients(
    client: FlaskClient, logged_in_therapist: User, fake_therapist_profile: Therapist
):
    response = client.get("/clients/")
    assert response.status_code == 200
    return


def test_get_client(client: FlaskClient, logged_in_client: User):
    response = client.get(f"clients/{logged_in_client.client.id}")
    assert response.status_code == 200
    return


def test_update_client_profile_success(
    client: FlaskClient, logged_in_client: User, fake_client_profile_data: dict
):
    initial_client_count = db.session.execute(
        db.select(db.func.count()).select_from(Client)
    ).scalar()

    response = client.post(
        f"clients/{logged_in_client.client.id}/update", data=fake_client_profile_data
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
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

    response = client.post(f"clients/{logged_in_client.client.id}/update", data={})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False and "errors" in data
    assert (
        db.session.execute(db.select(db.func.count()).select_from(Client)).scalar()
        == initial_client_count
    )
    return
