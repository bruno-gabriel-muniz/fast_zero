from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time


def test_get_token(client: TestClient, users):
    response = client.post(
        '/auth/token/',
        data={
            'username': users[0]['email'],
            'password': users[0]['clean_password'],
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_get_token_unauthorized(client: TestClient, users):
    # Incorret password

    response = client.post(
        '/auth/token/',
        data={'username': users[1]['email'], 'password': 'NotSecret'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    detail = response.json()['detail']

    assert detail == 'Incorrect email or password'

    # Incorret username / email

    response = client.post(
        '/auth/token/',
        data={'username': 'bob', 'password': users[1]['clean_password']},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    detail = response.json()['detail']

    assert detail == 'Incorrect email or password'


def test_token_expired_after_time(client: TestClient, users):
    with freeze_time('2000-01-01 00:00:00'):
        response = client.post(
            '/auth/token/',
            data={
                'username': users[1]['email'],
                'password': users[1]['clean_password'],
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2000-01-01 00:31:00'):
        response = client.put(
            '/users/2',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json()['detail'] == 'Could not validate credentials'


def test_refresh_token(client: TestClient, users, tokens):
    with freeze_time('2000-01-01 00:29:59'):
        response = client.post(
            '/auth/refresh_token/',
            headers={'Authorization': f'Bearer {tokens[1]}'},
            json={
                'username': users[1]['username'],
                'email': users[1]['email'],
                'password': users[1]['password'],
            },
        )
        token = response.json()

        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in token
        assert token['token_type'] == 'Bearer'


def test_token_expired_dont_refresh(client: TestClient, users):
    with freeze_time('2000-01-01 00:00:00'):
        response = client.post(
            '/auth/token/',
            data={
                'username': users[1]['email'],
                'password': users[1]['clean_password'],
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2000-01-01 00:30:01'):
        response = client.post(
            '/auth/refresh_token/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': users[1]['username'],
                'email': users[1]['email'],
                'password': users[1]['password'],
            },
        )
        data = response.json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert data['detail'] == 'Could not validate credentials'
