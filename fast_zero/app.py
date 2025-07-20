from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.schemas import message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=message)
def read_root():
    return {'message': 'Olá, mundo!'}


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_root_html():
    """
    Retorna o root no formato HTML
    """
    out = open('fast_zero/root.html', 'r', encoding='utf-8')
    return HTMLResponse(out.read(), status_code=HTTPStatus.OK)
