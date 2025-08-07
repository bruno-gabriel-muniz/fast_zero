from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import UserList, UserPublic, UserSchema
from fast_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_session)]
T_User = Annotated[Session, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
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


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def list_users(
    session: T_Session,
    current_user: T_User,
    skip: int = 0,
    limit: int = 100,
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()

    return {'users': users}


@router.get('/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(
    id: int,
    session: T_Session,
    current_user: T_User,
):
    user = session.scalar(select(User).where(User.id == id))

    if not user:
        raise HTTPException(HTTPStatus.NOT_FOUND, 'User Not Found')

    return user


@router.put('/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    id: int,
    user: UserSchema,
    session: T_Session,
    curr_user: T_User,
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


@router.delete('/{id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def delete_user(
    id: int,
    session: T_Session,
    curr_user: T_User,
):
    if curr_user.id != id:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(curr_user)
    session.commit()

    return curr_user
