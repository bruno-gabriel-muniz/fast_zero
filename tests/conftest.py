from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()

    return TestClient(app)


@pytest.fixture
def users(session):
    password_hash = (  # Hash of password -> secret
        '$argon2id$v=19$m=65536,t=3,p=4$3FYOAgaHUAqF+'
        + '+qNIY46hQ$cW7w7d+p0lxubGuewmxao69l4TuW4u9XTrkjo64wWow'
    )
    user_a = User('alice', 'alice@example.com', password_hash)
    user_b = User('bob', 'bob@example.com', password_hash)

    session.add(user_a)
    session.add(user_b)
    session.commit()

    out = [
        {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': password_hash,
            'clean_password': 'secret',
        },
        {
            'username': 'bob',
            'email': 'bob@example.com',
            'password': password_hash,
            'clean_password': 'secret',
        },
    ]

    return out


@pytest.fixture
def tokens(users, client):
    out: list[str] = [
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUBleGFtcGxl'
        + 'LmNvbSIsImV4cCI6MTc1NDUxMjg2OX0.U_CgW5azzvgirg3eA7vUnI_SzxKOjYQL8'
        + 'KnHIA8JdAU',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJib2JAZXhhbXBsZS5j'
        + 'b20iLCJleHAiOjE3NTQ1MTI4Njl9.6UDtnxEZNqsnU_WMbuyKUWZ3R2QZJNQoA3MF'
        + 'rqbbijM',
    ]

    return out


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
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
