from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fast_zero.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    token_type: str
    access_token: str


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState = Field(default=TodoState.todo)


class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class FilterTodos(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=15)
    description: str | None = Field(default=None, min_length=3, max_length=15)
    state: TodoState | None = None
    offset: int = 0
    limit: int = 100


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TodoState | None = None


class TodoList(BaseModel):
    todos: list[TodoPublic]
