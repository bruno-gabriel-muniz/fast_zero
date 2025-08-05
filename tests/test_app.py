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


def test_list_users(client, users):
    # Exec
    result = client.get('/users/')

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()['users']

    assert result[0]['id'] == 1
    assert result[0]['email'] == users[0]['email']
    assert result[1]['username'] == users[1]['username']


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


def test_update_user(client, users):
    # Exec
    id_test = 2
    result = client.put(
        f'/users/{id_test}',
        json={
            'username': 'teste',
            'email': 'teste@example.com',
            'password': 'secret',
        },
    )

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()

    assert result['id'] == id_test
    assert result['username'] == 'teste'


def test_update_user_conflict(client, users):
    result = client.put(
        '/users/1',
        json={
            'username': 'bob',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert result.status_code == HTTPStatus.CONFLICT
    assert result.json()['detail'] == 'Email Or Username Already Exist'


def test_update_user_not_found(client, users):
    # Exec
    result = client.put(
        '/users/3',
        json={
            'username': 'teste',
            'email': 'teste@example.com',
            'password': 'secret',
        },
    )

    # Assert
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client, users):
    # Exec
    result = client.delete('/users/2')

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()

    assert result['username'] == users[1]['username']
    assert result['email'] == users[1]['email']


def test_delete_user_not_found(client, users):
    # Exec
    result = client.delete('/users/3')

    # Assert
    assert result.status_code == HTTPStatus.NOT_FOUND
