from datetime import datetime
from http import HTTPStatus

import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.models import Todo, TodoState, User


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client: TestClient, tokens, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {tokens[0]}'},
            json={
                'title': 'Teste',
                'description': 'testar',
                'state': 'doing',
            },
        )

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data == {
        'id': 1,
        'title': 'Teste',
        'description': 'testar',
        'state': 'doing',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_without_filters(
    client: TestClient, session: AsyncSession, users: list[User], tokens
):
    expected_todos = 5

    session.add_all(
        TodoFactory.create_batch(expected_todos, user_id=users[0]['id'])
    )

    await session.commit()

    response = client.get(
        '/todos/', headers={'Authorization': f'Bearer {tokens[0]}'}
    )

    assert response.status_code == HTTPStatus.OK

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_with_title_filter(
    client: TestClient, session: AsyncSession, users: list[User], tokens
):
    others_todos = 4
    expected_todos = 1

    session.add_all(
        TodoFactory.create_batch(
            others_todos, title='normal', user_id=users[0]['id']
        )
    )
    session.add(TodoFactory(title='test', user_id=users[0]['id']))

    await session.commit()

    response = client.get(
        '/todos/?title=test',
        headers={'Authorization': f'Bearer {tokens[0]}'},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()['todos']

    assert len(data) == expected_todos

    for item in data:
        assert item['title'] == 'test'


@pytest.mark.asyncio
async def test_list_todos_with_description_filter(
    client: TestClient, session: AsyncSession, users: list[User], tokens
):
    others_todos = 3
    expected_todos = 2

    session.add_all(
        TodoFactory.create_batch(
            others_todos, description='normal', user_id=users[0]['id']
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, description='test', user_id=users[0]['id']
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?description=test',
        headers={'Authorization': f'Bearer {tokens[0]}'},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()['todos']

    assert len(data) == expected_todos

    for item in data:
        assert item['description'] == 'test'


@pytest.mark.asyncio
async def test_list_todos_with_state_filter(
    client: TestClient, session: AsyncSession, users: list[User], tokens
):
    others_todos = 3
    expected_todos = 2

    session.add_all(
        TodoFactory.create_batch(
            others_todos, state='done', user_id=users[0]['id']
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, state='doing', user_id=users[0]['id']
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?state=doing', headers={'Authorization': f'Bearer {tokens[0]}'}
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()['todos']

    assert len(data) == expected_todos

    for item in data:
        assert item['state'] == 'doing'


@pytest.mark.asyncio
async def test_list_todos_with_all_filers(
    client: TestClient, session: AsyncSession, users: list[User], tokens
):
    others_todos = 4
    expected_todos = 1

    session.add_all(
        TodoFactory.create_batch(
            others_todos, state='todo', user_id=users[0]['id']
        )
    )
    session.add(
        TodoFactory(
            state='doing',
            title='test',
            description='test',
            user_id=users[0]['id'],
        )
    )

    await session.commit()

    response = client.get(
        '/todos/?state=doing&title=test&description=test',
        headers={'Authorization': f'Bearer {tokens[0]}'},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()['todos']

    assert len(data) == expected_todos

    for item in data:
        assert item['state'] == 'doing'
        assert item['title'] == 'test'
        assert item['description'] == 'test'


@pytest.mark.asyncio
async def test_list_todos_with_invalid_title(client: TestClient, tokens):
    response = client.get(
        '/todos/?title=' + 'a' * 20,
        headers={'Authorization': f'Bearer {tokens[1]}'},
    )

    response2 = client.get(
        '/todos/?title=12', headers={'Authorization': f'Bearer {tokens[1]}'}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    assert response2.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_todo(
    client: TestClient,
    session,
    users,
    tokens,
):
    task = Todo('test', 'test remove', 'trash', users[0]['id'])
    session.add(task)
    await session.commit()

    response = client.delete(
        '/todos/1', headers={'Authorization': f'Bearer {tokens[0]}'}
    )

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json()['message'] == 'Task has been deleted sucessfully'


@pytest.mark.asyncio
async def test_delete_todo_error(
    client: TestClient,
    session,
    users,
    tokens,
):
    # Task of Other User
    task = Todo('test', 'test remove', 'trash', users[0]['id'])
    session.add(task)
    await session.commit()

    response = client.delete(
        '/todos/1', headers={'Authorization': f'Bearer {tokens[1]}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Task not Found'

    # Task not Exist

    response = client.delete(
        '/todos/2', headers={'Authorization': f'Bearer {tokens[1]}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Task not Found'


@pytest.mark.asyncio
async def test_update_todo(
    client: TestClient, users, tokens, session, mock_db_time
):
    with mock_db_time(model=Todo) as time1:
        todo = Todo('test', 'updating', 'doing', users[0]['id'])
        session.add(todo)
        await session.commit()

    with mock_db_time(model=Todo, time=datetime.now()) as time2:
        response = client.patch(
            '/todos/1',
            json={'state': 'done'},
            headers={'Authorization': f'Bearer {tokens[0]}'},
        )

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data == {
        'id': 1,
        'title': 'test',
        'description': 'updating',
        'state': 'done',
        'created_at': time1.isoformat(),
        'updated_at': time2.isoformat(),
    }


@pytest.mark.asyncio
async def test_update_todo_not_found_error(client, users, tokens, session):
    # Task of Other User
    task = Todo('test', 'updating', 'doing', users[0]['id'])
    session.add(task)
    await session.commit()

    response = client.patch(
        '/todos/1',
        json={'state': 'done'},
        headers={'Authorization': f'Bearer {tokens[1]}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json()['detail'] == 'Task not Found'

    # Task not Exist
    response = client.patch(
        '/todos/2',
        json={'state': 'done'},
        headers={'Authorization': f'Bearer {tokens[1]}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json()['detail'] == 'Task not Found'
