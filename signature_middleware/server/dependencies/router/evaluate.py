from fastapi import status, HTTPException, Path, Depends
from ...db import db
from ...authentication import get_signs_active_user
from ...models.initialize import Initialized
from ...models.terminal import Terminal
from ...models.intermediate import UpdateIntermediate, Intermediate
from ...models.authentication import User


async def before_create_intermediate_level(payload: Intermediate,
                                           current_user: User = Depends(get_signs_active_user)):
    if current_user.role != 'Super Admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to create level.')
    return payload


async def evaluate_duplication_intermediate(
        payload: Intermediate = Depends(before_create_intermediate_level),
        current_user: User = Depends(get_signs_active_user)
):
    if payload.channel_access_token:
        if await db.find_one(collection='intermediates',
                             query={'channel_access_token': payload.channel_access_token,
                                    'subject': payload.subject}) is None:
            if await db.find_one(collection='organizations',
                                 query={'channel_access_token': payload.channel_access_token}) is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='Something wrong please try again.')
            return payload
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Intermediate subject is duplicate.')


async def admin_via_fd_intermediate(
        channel_access_token: str = Path(description='revoke id document record in mongodb.'),
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role == 'Member':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to permission.')
    return channel_access_token


async def super_admin_via_find_intermediate(
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role != 'Super Admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to access.')
    return current_user


async def admin_via_find_intermediate(
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role == 'Member':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to access.')
    return current_user


async def permission_super_admin_via_find(
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role != 'Super Admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to access.')
    return current_user


async def permission_super_admin_via_create(
        payload: Initialized,
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role != 'Super Admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to permission.')
    return payload


async def evaluate_duplication_organization(
        payload: Initialized = Depends(permission_super_admin_via_create)
):
    validate_name_org = await db.find(collection='organizations',
                                      query={'channel_access_token': payload.channel_access_token})
    validate_name_org = list(validate_name_org)
    if len(validate_name_org) > 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Issued company duplicate.')
    return payload


async def admin_via_create_terminal(
        payload: Terminal,
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role == 'Member':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to permission.')
    return payload


async def admin_via_fd_terminal(
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role == 'Member':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to permission.')
    return id
