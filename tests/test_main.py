from flask.testing import FlaskClient


def test_get_index(client: FlaskClient):
    get_response = client.get("/")
    assert get_response.status_code == 200


def test_post_index(client: FlaskClient):
    post_response = client.post("/")
    assert post_response.status_code == 405
