import json
from typing import List, Union
from fastapi import APIRouter, Query, Path, HTTPException, status, Depends, \
    BackgroundTasks
from fastapi.encoders import jsonable_encoder
from ..db import db
from ..authentication import get_signs_active_user
from ..models.authentication import User
from ..models.initialize import Initialized, UpdateInitialize
from ..dependencies.router.log import log_transaction
from ..dependencies.router.evaluate import evaluate_duplication_organization, \
    permission_super_admin_via_find
from ..dependencies.redis_connection import init_redis

router = APIRouter()

COLLECTION = 'organizations'


@router.get('/find/organization', response_model=List[Initialized])
async def find_root(
        background_task: BackgroundTasks,
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start documents in collection'),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end documents in collection'),
        redis_conn=Depends(init_redis),
        current_user: User = Depends(permission_super_admin_via_find),
):
    key = f'organization:{skip}:{limit}'
    orgs = await redis_conn.get(key)
    if not orgs:
        stored_model = await db.find(collection=COLLECTION, query={})
        stored_model = stored_model.skip(skip).limit(limit)
        stored_model = list(stored_model)
        await redis_conn.set(key, json.dumps(stored_model))
        await redis_conn.expire(key, 300)
        if not stored_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
        background_task.add_task(
            log_transaction,
            method='/GET',
            endpoint='/initial/find/organization',
            from_cache=False,
            info_user=current_user.dict()
        )
        return stored_model

    background_task.add_task(
        log_transaction,
        method='/GET',
        endpoint='/initial/find/organization',
        from_cache=True,
        info_user=current_user.dict()
    )
    return json.loads(orgs)


@router.get('/find/organization/{id}', response_model=Initialized)
async def find_root_one(
        background_task: BackgroundTasks,
        id: str = Path(title='Document ID in collection for get item.',
                       regex='^(?![a-z])[a-z0-9]+$'),
        current_user: User = Depends(permission_super_admin_via_find),
        redis_conn=Depends(init_redis),
):
    org = await redis_conn.get(id)
    if not org:
        stored_model = await db.find_one(collection=COLLECTION, query={'_id': id})
        await redis_conn.set(id, json.dumps(stored_model))
        await redis_conn.expire(id, 300)
        if not stored_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
        background_task.add_task(
            log_transaction,
            method='/GET',
            endpoint=f'/initial/find/organization/{id}',
            from_cache=False,
            info_user=current_user.dict()
        )
        return stored_model

    background_task.add_task(
        log_transaction,
        method='/GET',
        endpoint=f'/initial/find/organization/{id}',
        from_cache=True,
        info_user=current_user.dict()
    )
    return json.loads(org)


@router.post('/issue/organization', response_model=Initialized)
async def create_root(
        background_task: BackgroundTasks,
        payload: Initialized = Depends(evaluate_duplication_organization),
        current_user: User = Depends(get_signs_active_user)
):
    item_model = jsonable_encoder(payload)
    await db.insert_one(collection=COLLECTION, data=item_model)
    background_task.add_task(
        log_transaction,
        method='/POST',
        endpoint='/initial/issue/organization',
        from_cache=False,
        payload=payload.dict(),
        info_user=current_user.dict()
    )
    return item_model


@router.put('/solve/organization/{id}', response_model=UpdateInitialize)
async def update_root(
        background_task: BackgroundTasks,
        id: str = Path(title='Document ID in collection for update item.',
                       regex='^(?![a-z])[a-z0-9]+$'),
        payload: Initialized = Depends(evaluate_duplication_organization),
        current_user: User = Depends(get_signs_active_user)
):
    item_model = jsonable_encoder(payload)
    query = {'_id': id}
    values = {'$set': item_model}
    if (await db.update_one(collection=COLLECTION,
                            query=query,
                            values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Not found {id} or update already exits.')
    background_task.add_task(
        log_transaction,
        method='/PUT',
        endpoint=f'/initial/solve/organization/{id}',
        from_cache=False,
        payload=payload.dict(),
        info_user=current_user.dict()
    )
    return item_model