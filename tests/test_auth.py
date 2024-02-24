from flask.testing import FlaskClient


def test_get_login(client: FlaskClient):
    get_response = client.get("/login")
    assert get_response.status_code == 200

