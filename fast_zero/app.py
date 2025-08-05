from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


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
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email Or Username Already Exist',
        )

    db_user = User(user.username, user.email, user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def list_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()

    return {'users': users}


@app.get('/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == id))

    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User Not Found')

    return user


@app.put('/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    id: int, user: UserSchema, session: Session = Depends(get_session)
):
    db_user = session.scalar(select(User).where(User.id == id))

    if not db_user:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User Not Found')

    invalid_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if invalid_user:
        raise HTTPException(
            HTTPStatus.CONFLICT, 'Email Or Username Already Exist'
        )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password

    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete(
    '/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == id))

    if not user_db:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User Not Found')

    session.delete(user_db)
    session.commit()

    return user_db
