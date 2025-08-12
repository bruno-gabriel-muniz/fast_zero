from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import Settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/auth/token', refreshUrl='/auth/refresh_token'
)
settings = Settings()

T_AsyncSession = Annotated[AsyncSession, Depends(get_session)]
Tr_oauth2_scheme = Annotated[str, Depends(oauth2_scheme)]


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})

    encode_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encode_jwt


async def get_current_user(
    session: T_AsyncSession,
    token: Tr_oauth2_scheme,
):
    credentials_exceptions = HTTPException(
        HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        subject_email = payload.get('sub')

        if not subject_email:
            raise credentials_exceptions

    except DecodeError:
        raise credentials_exceptions
    except ExpiredSignatureError:
        raise credentials_exceptions

    user = await session.scalar(
        select(User).where(User.email == subject_email)
    )

    if not user:
        # possivel falha de segurança
        # (token criado de forma indireta ou incorreta)
        raise credentials_exceptions

    return user
