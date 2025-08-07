from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from jwt import decode, encode

from fast_zero.security import create_access_token


def test_create_access_token(settings):
    test_data = {'test': 'test'}

    encoded = create_access_token(test_data)

    decoded = decode(encoded, settings.SECRET_KEY, settings.ALGORITHM)

    assert test_data['test'] == decoded['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Could not validate credentials'


def test_jwt_invalid_without_sub(client, settings):
    invalid_token = encode(
        {'exp': datetime.now(tz=ZoneInfo('UTC')) + timedelta(minutes=30)},
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {invalid_token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Could not validate credentials'


def test_jwt_invalid_sub(client, settings):
    invalid_token = encode(
        {
            'exp': datetime.now(tz=ZoneInfo('UTC')) + timedelta(minutes=30),
            'sub': 'nobody@example.com',
        },
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {invalid_token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Could not validate credentials'
