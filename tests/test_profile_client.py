from flask.testing import FlaskClient

from app import db
from app.models import User
from app.models.client import Client


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
