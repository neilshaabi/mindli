import random
from datetime import date
from typing import Any, Generator

import pytest
from faker import Faker
from flask import Flask
from flask.testing import FlaskClient
from flask_login import current_user
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.config import TestConfig
from app.models import SeedableMixin
from app.models.client import Client
from app.models.enums import Gender, Occupation, ReferralSource, UserRole
from app.models.intervention import Intervention
from app.models.issue import Issue
from app.models.language import Language
from app.models.therapist import Therapist
from app.models.title import Title
from app.models.user import User


@pytest.fixture(scope="session")
def app() -> Generator[Flask, Any, None]:
    app = create_app(config=TestConfig)
    with app.app_context():
        yield app
    return


@pytest.fixture(scope="session")
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope="session")
def fake() -> Generator[Faker, Any, None]:
    fake = Faker()
    yield fake
    return


@pytest.fixture(scope="session")
def seeded_data():
    seeded_data_dict = {}
    for model in SeedableMixin.__subclasses__():
        seeded_data_dict[model] = db.session.execute(db.select(model)).scalars().all()
    return seeded_data_dict


@pytest.fixture(scope="module")
def FAKE_PASSWORD() -> str:
    return "ValidPassword1"


@pytest.fixture(scope="module")
def fake_user_client(fake: Faker, FAKE_PASSWORD: str) -> Generator[User, Any, None]:
    fake_user_client = User(
        email=fake.unique.email().lower(),
        password_hash=generate_password_hash(FAKE_PASSWORD),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        gender=Gender.MALE,
        date_joined=fake.past_date(start_date="-1y", tzinfo=None),
        role=UserRole.CLIENT,
        verified=True,
        active=True,
    )
    db.session.add(fake_user_client)
    db.session.commit()

    yield fake_user_client

    db.session.delete(fake_user_client)
    db.session.commit()
    return


@pytest.fixture(scope="module")
def fake_user_therapist(FAKE_PASSWORD: str) -> Generator[User, Any, None]:
    fake_user_therapist = User(
        email="test_therapist@example.com".lower(),
        password_hash=generate_password_hash(FAKE_PASSWORD),
        first_name="Alice",
        last_name="Gray",
        date_joined=date.today(),
        role=UserRole.THERAPIST,
        verified=True,
        active=True,
    )
    db.session.add(fake_user_therapist)
    db.session.commit()

    yield fake_user_therapist

    db.session.delete(fake_user_therapist)
    db.session.commit()
    return


@pytest.fixture(scope="function")
def logged_in_client(
    client: FlaskClient, fake_user_client: User, FAKE_PASSWORD: str
) -> Generator[User, Any, None]:
    with client:
        response = client.post(
            "/login",
            data={
                "email": fake_user_client.email,
                "password": FAKE_PASSWORD,
            },
        )
        assert response.status_code == 200
        assert current_user.is_authenticated

        yield fake_user_client

        client.get("/logout")
        return


@pytest.fixture(scope="function")
def logged_in_therapist(
    client: FlaskClient, fake_user_therapist: User, FAKE_PASSWORD: str
) -> Generator[User, Any, None]:
    with client:
        response = client.post(
            "/login",
            data={
                "email": fake_user_therapist.email,
                "password": FAKE_PASSWORD,
            },
        )

        assert response.status_code == 200
        assert current_user.is_authenticated

        yield fake_user_therapist

        client.get("/logout")
    return


@pytest.fixture(scope="module")
def fake_registration_data(fake_user_client: User, FAKE_PASSWORD: str) -> dict:
    return {
        "role": fake_user_client.role.value,
        "first_name": fake_user_client.first_name,
        "last_name": fake_user_client.last_name,
        "email": f"new-{fake_user_client.email}",
        "password": FAKE_PASSWORD,
    }


@pytest.fixture(scope="module")
def fake_therapist_profile(
    fake_user_therapist: User,
) -> Generator[Therapist, Any, None]:
    fake_therapist_profile = Therapist(
        user_id=fake_user_therapist.id,
        country="Singapore",
        location="21 Lower Kent Ridge Rd, Singapore 119077",
        years_of_experience=5,
        qualifications="Doctor of Psychology in Clinical Psychology, NUS",
        registrations="Singapore Psychological Society (SPS)",
    )
    db.session.add(fake_therapist_profile)
    db.session.commit()

    yield fake_therapist_profile
    return


@pytest.fixture(scope="module")
def fake_client_profile(
    fake: Faker, seeded_data: dict, fake_user_client: User
) -> Generator[Client, Any, None]:
    fake_client = Client(
        user_id=fake_user_client.id,
        date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=65),
        occupation=random.choice(list(Occupation)),
        address=fake.address(),
        phone="+6581234567",
        emergency_contact_name=fake.name(),
        emergency_contact_phone="+6581234567",
        referral_source=random.choice(list(ReferralSource)),
        issues=random.sample(
            seeded_data[Issue], random.randint(1, min(3, len(seeded_data[Issue])))
        ),
    )
    db.session.add(fake_client)
    db.session.commit()

    yield fake_client
    return


@pytest.fixture(scope="module")
def fake_therapist_profile_data(
    fake_therapist_profile: Therapist, seeded_data: dict
) -> dict:
    return {
        "titles": [title.id for title in seeded_data[Title]][:2],
        "years_of_experience": fake_therapist_profile.years_of_experience,
        "qualifications": fake_therapist_profile.qualifications,
        "registrations": fake_therapist_profile.registrations,
        "country": fake_therapist_profile.country,
        "location": fake_therapist_profile.location,
        "languages": [language.id for language in seeded_data[Language]][:2],
        "issues": [issue.id for issue in seeded_data[Issue]][:2],
        "interventions": [
            intervention.id for intervention in seeded_data[Intervention]
        ][:2],
        "link": fake_therapist_profile.link,
    }


@pytest.fixture(scope="module")
def fake_client_profile_data(seeded_data: dict) -> dict:
    return {
        "date_of_birth": "1990-01-01",
        "occupation": Occupation.STUDENT.name,
        "address": "123 Main St, Anytown, AT 12345",
        "phone": "+6585781481",
        "emergency_contact_name": "Jane Doe",
        "emergency_contact_phone": "+6596697927",
        "referral_source": ReferralSource.OTHER.name,
        "issues": [issue.id for issue in seeded_data[Issue]][:2],
        "consent": True,
    }
