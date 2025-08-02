from dataclasses import asdict
from datetime import datetime

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='alice', email='alice@example.com', password='secret'
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'alice'))

    assert asdict(user) == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }


def test_update_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='Alice', email='alice@example.com', password='secret'
        )

        session.add(new_user)
        session.commit()

    with mock_db_time(model=User, time=datetime.now()) as time1:
        user = session.scalar(
            select(User).where(User.email == 'alice@example.com')
        )

        user.username = 'alice'
        session.commit()

        user = session.scalar(
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
