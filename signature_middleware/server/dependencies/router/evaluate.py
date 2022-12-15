from fastapi import status, HTTPException, Query, Depends
from ...db import db
from ...authentication import get_signs_active_user
from ...models.initialize import Initialized
from ...models.intermediate import Intermediate
from ...models.authentication import User


async def before_create_intermediate_level(payload: Intermediate,
                                           current_user: User = Depends(get_signs_active_user)):
    if current_user.role != 'Admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not allow to create level.')
    return payload


async def evaluate_duplication_intermediate(
        payload: Intermediate = Depends(before_create_intermediate_level)
):
    if await db.find_one(collection='certificates',
                         query={'name': payload.name}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Intermediate name is duplicate.')
    return payload


async def permission_super_admin_via_revoke(
        id: str = Query(..., description='revoke id document record in mongodb.'),
        current_user: User = Depends(get_signs_active_user)
):
    if current_user.role != 'Super Admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not allow to purge level.')
    return id


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


async def evaluate_duplication_company_name(
        payload: Initialized = Depends(permission_super_admin_via_create)
):
    if await db.find_one(collection='certificates',
                         query={'company_name': payload.company_name}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Company name is duplicate.')
    return payload
