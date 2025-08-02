from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fast_zero.app import app, db_fake
from fast_zero.models import table_registry


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


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(*, model, time=datetime.now()):
    def fake_time_hook_created(mapper, conection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    def fake_time_hook_updated(mapper, connection, target):
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook_created)
    event.listen(model, 'before_update', fake_time_hook_updated)

    yield time

    event.remove(model, 'before_insert', fake_time_hook_created)
    event.remove(model, 'before_update', fake_time_hook_updated)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
