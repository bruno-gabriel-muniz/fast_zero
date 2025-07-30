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


def test_read_users(client, db):
    # Exec
    result = client.get('/users/')

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()['users']

    assert result[0]['id'] == 1
    assert result[0]['email'] == 'alice@example.com'
    assert result[1]['username'] == 'bob'


def test_get_user(client, db):
    # Exec
    result = client.get(
        '/users/1',
    )

    # Assert
    assert result.status_code == HTTPStatus.OK

    result = result.json()

    assert result['username'] == 'alice'


def test_get_user_not_found(client, db):
    result = client.get('/users/3')

    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_user(client, db):
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


def test_update_user_not_found(client, db):
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


def test_delete_user(client, db):
    # Exec
    result = client.delete('/users/2')

    # Assert
    assert result.status_code == HTTPStatus.OK
    assert len(db) == 1

    result = result.json()

    assert result['username'] == 'bob'


def test_delete_user_not_found(client, db):
    # Exec
    result = client.delete('/users/3')

    # Assert
    assert result.status_code == HTTPStatus.NOT_FOUND
