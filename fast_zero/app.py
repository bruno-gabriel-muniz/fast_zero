from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

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

    db_user = User(user.username, user.email, get_password_hash(user.password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def list_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
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
    id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    curr_user: User = Depends(get_current_user),
):
    if curr_user.id != id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    invalid_user = session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if invalid_user.id != curr_user.id:
        raise HTTPException(
            HTTPStatus.CONFLICT, 'Email Or Username Already Exist'
        )

    curr_user.username = user.username
    curr_user.email = user.email
    curr_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(curr_user)

    return curr_user


@app.delete(
    '/users/{id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def delete_user(
    id: int,
    session: Session = Depends(get_session),
    curr_user: User = Depends(get_current_user),
):
    if curr_user.id != id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(curr_user)
    session.commit()

    return curr_user


@app.post('/token/', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not (user and verify_password(form_data.password, user.password)):
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='Incorrect email or password'
        )

    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
