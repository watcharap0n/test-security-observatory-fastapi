from fastapi import status, HTTPException, Path, Depends
from ...db import db
from ...authentication import get_signs_active_user
from ...models.initialize import Initialized
from ...models.intermediate import UpdateIntermediate, Intermediate
from ...models.authentication import User


async def before_create_intermediate_level(payload: Intermediate,
                                           current_user: User = Depends(get_signs_active_user)):
    if current_user.role == 'Member':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not allow to create level.')
    return payload


async def evaluate_duplication_intermediate(
        payload: UpdateIntermediate = Depends(before_create_intermediate_level),
        current_user: User = Depends(get_signs_active_user)
):
    if await db.find_one(collection='intermediates',
                         query={'channel_access_token': current_user.channel_access_token,
                                'subject': payload.subject}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Intermediate subject is duplicate.')
    return payload


async def admin_via_fd_intermediate(
        id: str = Path(description='revoke id document record in mongodb.',
                       regex='^(?![a-z])[a-z0-9]+$'),
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role == 'Member':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not allow to purge level.')
    return id


async def admin_via_find_intermediate(
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role == 'Member':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not allow to access.')
    return current_user


async def permission_super_admin_via_find(
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role != 'Super Admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not allow to access.')
    return current_user


async def permission_super_admin_via_create(
        payload: Initialized,
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role != 'Super Admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not allow to purge level.')
    return payload


async def evaluate_duplication_organization(
        payload: Initialized = Depends(permission_super_admin_via_create)
):
    if await db.find_one(collection='certificates',
                         query={'organization': payload.organization}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Company name is duplicate.')
    return payload


async def permission_access_terminal_cert(
        id: str = Path(description='ID document terminal cert'),
        current_user: User = Depends(get_signs_active_user)
):
    if (await db.find_one(collection='terminals',
                          query={'owner.uid': current_user.uid})) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not allow to access denies')
    return id
