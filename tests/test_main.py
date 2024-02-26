from flask.testing import FlaskClient


def test_get_index(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200
    return


def test_post_index(client: FlaskClient):
    response = client.post("/")
    assert response.status_code == 200
    assert "error" in response.get_data(as_text=True).lower()
    return


def test_get_error(client: FlaskClient):
    response = client.get("/error")
    assert response.status_code == 200
    assert "error" in response.get_data(as_text=True).lower()
    return
