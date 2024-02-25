from flask.testing import FlaskClient


def test_get_index(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200


def test_post_index(client: FlaskClient):
    response = client.post("/")
    assert response.status_code == 405
