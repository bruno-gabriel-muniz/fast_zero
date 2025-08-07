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
