from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_root_retorna_ola_mundo():
    """
    Teste incial do app.
    """
    # Set Up
    client = TestClient(app)

    # Execute
    response = client.get('/')

    # Assert
    assert response.json()['message'] == 'Olá, mundo!'
    assert response.status_code == HTTPStatus.OK


def test_root_html_retorna_html():
    """
    Teste da devolução no formato de APIRest
    """
    # Set Up
    client = TestClient(app)

    # Execute
    response = client.get('/html')

    # Asserte
    expected = open('fast_zero/root.html', 'r', encoding='utf-8')
    assert response.text == expected.read()
    assert response.status_code == HTTPStatus.OK
