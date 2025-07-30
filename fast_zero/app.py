from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

db_fake = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá, mundo!'}


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_root_html():
    """
    Retorna o root no formato HTML
    """
    out = open('fast_zero/root.html', 'r', encoding='utf-8')
    return HTMLResponse(out.read(), status_code=HTTPStatus.OK)


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user = UserDB(**user.model_dump(), id=len(db_fake) + 1)

    db_fake.append(user)

    return user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def list_users():
    return {'users': db_fake}


@app.get('/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(id: int):
    if id < 1 or len(db_fake) < id:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')

    return db_fake[id - 1]


@app.put('/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(id: int, user: UserSchema):
    user = UserDB(**user.model_dump(), id=id)

    if id < 1 or len(db_fake) < id:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')

    db_fake[id - 1] = user

    return user


@app.delete(
    '/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(id: int):
    if id < 1 or len(db_fake) < id:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='User not found')

    user = db_fake[id - 1]

    db_fake.pop(id - 1)

    return user
