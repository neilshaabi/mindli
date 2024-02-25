from datetime import date
from typing import Any, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.config import TestConfig
from app.models import Gender, User, UserRole


@pytest.fixture(scope='module')
def app() -> Generator[Flask, Any, None]:
    
    app = create_app(config=TestConfig)
    
    with app.app_context():
        db.create_all()
        
        yield app
        
        db.session.remove()
        db.drop_all()
    return


@pytest.fixture(scope='module')
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope='function')
def fake_user_password() -> str:
    return 'ValidPassword1'


@pytest.fixture(scope='function')
def fake_user_client(fake_user_password: str) -> Generator[User, Any, None]:
    
    # Insert test data
    fake_user_client = User(
            email="client@example.com".lower(),
            password_hash=generate_password_hash(fake_user_password),
            first_name="John",
            last_name="Smith",
            date_joined=date.today(),
            role=UserRole.CLIENT,
            verified=True,
            active=True,
            gender=Gender.MALE,
        )
    db.session.add(fake_user_client)
    db.session.commit()
    
    yield fake_user_client
    
    db.session.delete(fake_user_client)
    db.session.commit()
    return

