from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    FilterTodos,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_User = Annotated[User, Depends(get_current_user)]
T_FilterTodos = Annotated[FilterTodos, Query()]


@router.post('/', response_model=TodoPublic)
async def create_todo(todo: TodoSchema, session: T_Session, user: T_User):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
async def list_todo(
    filter: T_FilterTodos,
    session: T_Session,
    user: T_User,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if filter.title:
        query = query.filter(Todo.title.contains(filter.title))

    if filter.description:
        query = query.filter(Todo.description.contains(filter.description))

    if filter.state:
        query = query.filter(Todo.state == filter.state)

    todos = await session.scalars(
        query.limit(filter.limit).offset(filter.offset)
    )

    return {'todos': todos.all()}


@router.delete(
    '/{id}', status_code=HTTPStatus.ACCEPTED, response_model=Message
)
async def delete_todo(
    id: int,
    user: T_User,
    session: T_Session,
):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == id)
    )

    if not todo:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='Task not Found')

    await session.delete(todo)

    return Message(message='Task has been deleted sucessfully')


@router.patch('/{id}', status_code=HTTPStatus.OK, response_model=TodoPublic)
async def update_tudo(
    id: int, session: T_Session, user: T_User, todo: TodoUpdate
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == id)
    )

    if not db_todo:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='Task not Found')

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo
