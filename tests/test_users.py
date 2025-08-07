from http import HTTPStatus


def test_create_user(client):
    # Exec
    current_id = 1
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    # Assert
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id'] == current_id
    assert response.json()['username'] == 'alice'

    # Exec
    current_id += 1
    response = client.post(
        '/users/',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'secret',
        },
    )

    # Assert
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id'] == current_id
    assert response.json()['username'] == 'bob'


def test_create_user_conflict(client, users):
    result = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert result.status_code == HTTPStatus.CONFLICT
    assert result.json()['detail'] == 'Email Or Username Already Exist'


def test_list_users(client, users, tokens):
    # Exec
    result = client.get(
        '/users/', headers={'Authorization': f'Bearer {tokens[0]}'}
    )

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()['users']

    assert result[0]['id'] == 1
    assert result[0]['email'] == users[0]['email']
    assert result[1]['username'] == users[1]['username']


def test_get_user(client, users, tokens):
    # Exec
    result = client.get(
        '/users/2', headers={'Authorization': f'Bearer {tokens[0]}'}
    )

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()

    assert result['username'] == users[1]['username']


def test_get_user_not_found(client, users, tokens):
    result = client.get(
        '/users/3', headers={'Authorization': f'Bearer {tokens[1]}'}
    )

    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, users, tokens):
    # Exec
    result = client.put(
        '/users/1',
        json={
            'username': 'teste',
            'email': 'alice@example.com',
            'password': 'secret',
        },
        headers={'Authorization': f'Bearer {tokens[0]}'},
    )

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()

    assert result['id'] == 1
    assert result['username'] == 'teste'


def test_update_user_conflict(client, users, tokens):
    result = client.put(
        '/users/2',
        json={
            'username': 'bob',
            'email': 'alice@example.com',
            'password': 'secret',
        },
        headers={'Authorization': f'Bearer {tokens[1]}'},
    )

    assert result.status_code == HTTPStatus.CONFLICT
    assert result.json()['detail'] == 'Email Or Username Already Exist'


def test_update_user_forbidden(client, users, tokens):
    response = client.put(
        '/users/1',
        json={
            'username': 'name',
            'email': 'alice@example.com',
            'password': 'secret',
        },
        headers={'Authorization': f'Bearer {tokens[1]}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'] == 'Not enough permissions'


def test_delete_user(client, users, tokens):
    # Exec
    result = client.delete(
        '/users/2',
        headers={'Authorization': f'Bearer {tokens[1]}'},
    )

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()

    assert result['username'] == users[1]['username']
    assert result['email'] == users[1]['email']


def test_delete_user_forbidden(client, users, tokens):
    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {tokens[1]}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()['detail'] == 'Not enough permissions'
