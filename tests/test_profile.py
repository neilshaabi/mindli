from flask.testing import FlaskClient

from app.models import User


def test_get_profile_unauthenticated(client: FlaskClient):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    return

def test_get_profile(client: FlaskClient, logged_in_therapist: User):
    response = client.get("/profile")
    assert response.status_code == 200
    return
