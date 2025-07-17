from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_root_retorna_ola_mundo():
    """
    Teste incial do app.
    """
    # Set Up
    client = TestClient(app)

    # execute
    response = client.get('/')

    # Assert
    assert response.json()['message'] == 'Olá, mundo!'
    assert response.status_code == HTTPStatus.OK
