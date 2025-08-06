from http import HTTPStatus


def test_root_retorna_ola_mundo(client):
    # Execute
    response = client.get('/')

    # Assert
    assert response.json()['message'] == 'Olá, mundo!'
    assert response.status_code == HTTPStatus.OK


def test_root_html_retorna_html(client):
    # Execute
    response = client.get('/html')

    # Asserte
    expected = open('fast_zero/root.html', 'r', encoding='utf-8')
    assert response.text == expected.read()
    assert response.status_code == HTTPStatus.OK


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


# TODO: update


def test_get_user(client, users):
    # Exec
    result = client.get(
        '/users/1',
    )

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()

    assert result['username'] == users[0]['username']


def test_get_user_not_found(client, users):
    result = client.get('/users/3')

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


def test_get_token(client, users):
    response = client.post(
        '/token/',
        data={
            'username': users[0]['email'],
            'password': users[0]['clean_password'],
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_get_token_unauthorized(client, users):
    # Incorret password

    response = client.post(
        '/token/',
        data={'username': users[1]['email'], 'password': 'NotSecret'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    detail = response.json()['detail']

    assert detail == 'Incorrect email or password'

    # Incorret username / email

    response = client.post(
        '/token/',
        data={'username': 'bob', 'password': users[1]['clean_password']},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    detail = response.json()['detail']

    assert detail == 'Incorrect email or password'
