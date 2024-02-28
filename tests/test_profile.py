from flask.testing import FlaskClient

from app.models import User
from app import db
from app.models.therapist import Therapist
from tests.conftest import post_with_csrf

# def test_get_profile_unauthenticated(client: FlaskClient):
#     response = client.get("/profile")
#     assert response.status_code == 302
#     assert "/login" in response.headers["Location"]
#     return


# def test_get_profile(client: FlaskClient, logged_in_therapist: User):
#     response = client.get("/profile")
#     assert response.status_code == 200
#     return


def test_update_therapist_profile_success(client, logged_in_therapist: User, therapist_profile_data: dict):
    initial_therapist_count = db.session.execute(
        db.select(db.func.count()).select_from(Therapist)
    ).scalar()

    response = post_with_csrf(client=client, url="/profile", data=therapist_profile_data)
    data = response.get_json()

    assert response.status_code == 200

    assert data["success"] is True
    assert "url" in data

    # Verify that a new Therapist profile has been created in the database
    new_therapist_count = db.session.execute(
        db.select(db.func.count()).select_from(Therapist)
    ).scalar()
    assert new_therapist_count == initial_therapist_count + 1

    # Additional checks can include verifying the contents of the newly created Therapist profile
    # to ensure that the submitted data has been correctly saved to the database.



# def test_profile_update_missing_fields(client, logged_in_therapist: User, therapist_profile_data: dict):
    
#     initial_therapist_count = db.session.execute(
#         db.select(db.func.count()).select_from(Therapist)
#     ).scalar()

#     # response = post_with_csrf(client=client, url="/profile", data={})
#     response = client.post("/profile", data={})
#     data = response.get_json()

#     assert response.status_code == 200
#     assert data["success"] is False
#     assert "errors" in data
#     assert set(data["errors"]) == set(therapist_profile_data.keys())
#     assert (
#         db.session.execute(db.select(db.func.count()).select_from(Therapist)).scalar()
#         == initial_therapist_count
#     )
#     return
