from flask.testing import FlaskClient


def test_get_index(client: FlaskClient):
    """
    GIVEN a Flask client configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    get_response = client.get("/")
    assert get_response.status_code == 200


def test_post_index(client: FlaskClient):
    """
    GIVEN a Flask client configured for testing
    WHEN the '/' page is requested (POST)
    THEN check that the response is forbidden
    """
    post_response = client.post("/")
    assert post_response.status_code == 405
