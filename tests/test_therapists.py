from flask.testing import FlaskClient
from app.models import User


def test_get_therapist_profile(logged_in_therapist: User, client: FlaskClient):
    response = client.get("/therapists/")
    assert response.status_code == 200
    return


def test_update_therapist_profile_success(
    client: FlaskClient, logged_in_therapist: User, fake_therapist_profile_data: dict
):
    response = client.post(
        f"therapists/{logged_in_therapist.therapist.id}/update",
        data=fake_therapist_profile_data,
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    return


def test_update_therapist_profile_missing_fields(
    client: FlaskClient, logged_in_therapist: User
):
    response = client.post(
        f"therapists/{logged_in_therapist.therapist.id}/update", data={}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False and "errors" in data
    return
