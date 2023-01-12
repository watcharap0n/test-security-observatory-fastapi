from typing import List, Union, Optional
from fastapi import APIRouter, status, HTTPException, Path, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ..db import db
from ..authentication import get_signs_active_user
from ..models.intermediate import Intermediate, ChannelAccess, UpdateIntermediate
from ..models.authentication import User
from ..dependencies.router.evaluate import evaluate_duplication_intermediate, \
    admin_via_fd_intermediate, admin_via_find_intermediate

router = APIRouter()

COLLECTION = 'intermediates'


@router.post('/issue/level', response_model=Union[ChannelAccess, Intermediate],
             status_code=status.HTTP_201_CREATED)
async def create_intermediate_level(
        payload: Intermediate = Depends(evaluate_duplication_intermediate),
        current_user: User = Depends(get_signs_active_user)
):
    item_model = jsonable_encoder(payload)
    if payload.channel_access_token is None:
        item_stored = ChannelAccess(**item_model)
        item_stored.channel_access_token = current_user.channel_access_token
        await db.insert_one(collection=COLLECTION, data=jsonable_encoder(item_stored))
        return item_stored
    company_item = await db.find_one(collection='organizations',
                                     query={'channel_access_token': payload.channel_access_token})
    item_model['detail']['signerProfileName'] = company_item['detail']['profileName']
    item_model['detail']['signerPassword'] = company_item['detail']['password']
    await db.insert_one(collection=COLLECTION, data=item_model)
    return item_model


@router.get('/find/level/{channel_access_token}', response_model=List[Intermediate])
async def find_intermediates_via_admin(
        channel_access_token: str = Depends(admin_via_fd_intermediate),
        type: Optional[str] = Query(None, description='Query find all or find one.')
):
    exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                              detail='You are not issuing intermediate certificates.')
    if type:
        stored_model = await db.find(collection=COLLECTION,
                                     query={
                                         'channel_access_token': channel_access_token,
                                         'type': type
                                     })
        if not stored_model:
            raise exception
        return list(stored_model)
    stored_model = await db.find(collection=COLLECTION,
                                 query={'channel_access_token': channel_access_token})
    stored_model = list(stored_model)
    if not stored_model:
        raise exception
    return stored_model


@router.get('/find/level', response_model=List[Intermediate])
async def find_intermediates(
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start documents in collection'),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end documents in collection'),
        current_user: User = Depends(admin_via_fd_intermediate)
):
    stored_model = await db.find(collection=COLLECTION, query={})
    stored_model = stored_model.skip(skip).limit(limit)
    stored_model = list(stored_model)
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='You are not issuing intermediate certificates.')
    return stored_model


@router.get('/find/channel', response_model=List[Intermediate])
async def find_intermediate_channel(
        type: Union[bool, None] = Query(default=False, title='Query type intermediate selection.'),
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start documents in collection'),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end documents in collection'),
        current_user: User = Depends(admin_via_find_intermediate)
):
    # Exception query param to database backend with type personal
    query = dict()
    if type:
        query['type'] = 'personal'
    query['channel_access_token'] = current_user.channel_access_token
    # ===================== Query type ===================== #

    stored_model = await db.find(
        collection=COLLECTION,
        query=query
    )
    stored_model = stored_model.skip(skip).limit(limit)
    stored_model = list(stored_model)
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='You are not issuing intermediate certificates.')
    return stored_model


@router.put('/solve/level/{id}', response_model=UpdateIntermediate)
async def edit_intermediate_level(
        payload: UpdateIntermediate = Depends(evaluate_duplication_intermediate),
        id: str = Path(..., title='Query to transaction.',
                       regex='^(?![a-z])[a-z0-9]+$'),
):
    item_model = jsonable_encoder(payload)
    query_intermediate = {'_id': id}
    values = {'$set': item_model}
    if (await db.update_one(collection=COLLECTION,
                            query=query_intermediate,
                            values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Not found {id} or update already exits.')
    return item_model


@router.delete('/purge/level/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def purge_intermediate_level(
        id: str = Depends(admin_via_fd_intermediate)
):
    if (await db.delete_one(collection=COLLECTION, query={'_id': id})) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Intermediate cert is not found {id}."
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={'status': 'success'})
