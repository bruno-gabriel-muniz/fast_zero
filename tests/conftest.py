import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app, db_fake


@pytest.fixture
def client():
    db_fake.clear()
    return TestClient(app)


@pytest.fixture
def db():
    # SetUp
    db_fake.append({
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    })
    db_fake.append({
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 2,
    })
    return db_fake
