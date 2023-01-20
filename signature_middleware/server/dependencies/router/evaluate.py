from fastapi import status, HTTPException, Path, Depends
from ...db import db
from ...authentication import get_signs_active_user
from ...models.initialize import Initialized
from ...models.authentication import User


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


async def admin_via_fd_terminal(
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role == 'Member':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough to permission.')
    return id
