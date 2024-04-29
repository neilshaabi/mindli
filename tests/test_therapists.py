from flask.testing import FlaskClient

from app.models import User
from app.models.therapist import Therapist


def test_get_therapists(logged_in_therapist: User, client: FlaskClient):
    response = client.get("/therapists/")
    assert response.status_code == 200
    return


def test_get_therapist(
    logged_in_therapist: User, fake_therapist_profile: Therapist, client: FlaskClient
):
    response = client.get(f"/therapists/{logged_in_therapist.therapist.id}")
    assert response.status_code == 200
    return


def test_update_therapist_profile_success(
    client: FlaskClient,
    logged_in_therapist: User,
    fake_therapist_profile: Therapist,
    fake_therapist_profile_data: dict,
):
    response = client.post(
        f"therapists/{fake_therapist_profile.id}/update",
        data=fake_therapist_profile_data,
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    return


def test_update_therapist_profile_missing_fields(
    client: FlaskClient,
    logged_in_therapist: User,
    fake_therapist_profile: Therapist,
):
    response = client.post(f"therapists/{fake_therapist_profile.id}/update", data={})
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False and "errors" in data
    return
