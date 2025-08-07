from http import HTTPStatus


def test_get_token(client, users):
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


def test_get_token_unauthorized(client, users):
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
