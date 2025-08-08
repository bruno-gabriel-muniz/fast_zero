from dataclasses import asdict
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.models import User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='alice', email='alice@example.com', password='secret'
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'alice')
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_update_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Alice', email='alice@example.com', password='secret'
        )

        session.add(new_user)
        await session.commit()

    with mock_db_time(model=User, time=datetime.now()) as time1:
        user = await session.scalar(
            select(User).where(User.email == 'alice@example.com')
        )

        user.username = 'alice'
        await session.commit()

        user = await session.scalar(
            select(User).where(User.email == 'alice@example.com')
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time1,
    }
