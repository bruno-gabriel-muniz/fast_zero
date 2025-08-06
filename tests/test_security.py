from jwt import decode

from fast_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_create_access_token():
    test_data = {'test': 'test'}

    encoded = create_access_token(test_data)

    decoded = decode(encoded, SECRET_KEY, ALGORITHM)

    assert test_data['test'] == decoded['test']
    assert 'exp' in decoded
