import os
from typing import Union
from datetime import datetime, timedelta
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException, Security, status
from jose import JWTError, jwt
from fastapi.encoders import jsonable_encoder
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from passlib.context import CryptContext
from .db import db
from .models.authentication import User, UserInDB, Register, Token, TokenData
from .dependencies.authorize.header import signature_jwt_header

SECOND = 60
MINUTE = os.environ.get('EXPIRES_TOKEN', '60')
EXPIRES_TOKEN = SECOND * eval(MINUTE)
SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'
COLLECTION = 'authentication'

authenticate = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/jwt/auth/token',
    scopes={
        'me': 'Read information about the current user.',
        'signs': 'Read information apis signing.',
        'items': 'Read infomation another APIs.'},
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str):
    user_db = await db.find_one(collection=COLLECTION, query={'username': username})
    if user_db:
        return UserInDB(**user_db)


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid username or not register.')
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Invalid password please try again.')
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_scopes = payload.get('scopes', [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Not enough permissions',
                headers={'WWW-Authenticate': authenticate_value},
            )
    return user


async def get_current_active_user(
        current_user: User = Security(get_current_user, scopes=['me'])
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Inactive user')
    return current_user


async def get_signs_active_user(
        current_user: User = Security(get_current_user, scopes=['signs'])
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Inactive user')
    if current_user.role == 'Expire':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Please contact admin service.')
    return current_user


@authenticate.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect username or password')
    access_token_expires = timedelta(minutes=EXPIRES_TOKEN)
    access_token = create_access_token(
        data={'sub': user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return {'access_token': access_token, "token_type": "bearer"}


async def evaluate_duplicate_account(register: Register):
    if await db.find_one(collection=COLLECTION, query={'username': register.username}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exist.')
    return register


@authenticate.post('/register', response_model=Register)
async def register_user(
        register: Register = Depends(evaluate_duplicate_account),
        x_token: None = Depends(signature_jwt_header)):
    hashed = get_password_hash(register.hashed_password)
    register.hashed_password = hashed
    item_model = jsonable_encoder(register)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return item_model


@authenticate.get('/users/me/', response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@authenticate.get('/status/')
async def read_system_status(current_user: User = Depends(get_current_user)):
    return {'status': 'ok', 'service': 'e-signature demo'}