from contextlib import contextmanager
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from jwt import encode
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.settings import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def client(session: AsyncSession):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()

    return TestClient(app)


@pytest_asyncio.fixture
async def users(session: AsyncSession):
    password_hash = (  # Hash of password -> secret
        '$argon2id$v=19$m=65536,t=3,p=4$3FYOAgaHUAqF+'
        + '+qNIY46hQ$cW7w7d+p0lxubGuewmxao69l4TuW4u9XTrkjo64wWow'
    )
    user_a = User('alice', 'alice@example.com', password_hash)
    user_b = User('bob', 'bob@example.com', password_hash)

    session.add(user_a)
    session.add(user_b)
    await session.commit()

    out = [
        {
            'id': 1,
            'username': 'alice',
            'email': 'alice@example.com',
            'password': password_hash,
            'clean_password': 'secret',
        },
        {
            'id': 2,
            'username': 'bob',
            'email': 'bob@example.com',
            'password': password_hash,
            'clean_password': 'secret',
        },
    ]

    return out


@pytest.fixture
def tokens(users, settings):
    out: list[str] = []
    for user in users:
        token = encode(
            {
                'sub': user['email'],
                'exp': datetime.now(ZoneInfo('UTC')) + timedelta(minutes=30),
            },
            settings.SECRET_KEY,
            settings.ALGORITHM,
        )
        out.append(token)

    return out


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:latest', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


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
