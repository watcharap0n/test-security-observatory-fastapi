from typing import List, Union
from fastapi import status, HTTPException, Depends, APIRouter, Query, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from ..db import db
from ..models.terminal import Terminal, UpdateTerminal
from ..models.authentication import User
from ..authentication import get_signs_active_user
from ..dependencies.router.evaluate import admin_via_find_intermediate, admin_via_create_terminal, admin_via_fd_terminal

router = APIRouter()

COLLECTION = 'terminals'


@router.get('/find/cert', response_model=List[Terminal])
async def find_terminal_certs(
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start documents in collection'),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end documents in collection'),
        current_user: User = Depends(admin_via_find_intermediate),
        type: Union[bool, None] = False
):
    if type:
        terminals = await db.find(
            collection=COLLECTION,
            query={
                'imd_detail.channel_access_token': current_user.channel_access_token,
                'imd_detail.type': 'group'
            })
        stored_model = terminals.skip(skip).limit(limit)
        stored_model = list(stored_model)
        if not stored_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
        return stored_model
    terminals = await db.find(
        collection=COLLECTION,
        query={
            'imd_detail.channel_access_token': current_user.channel_access_token,
        })
    stored_model = terminals.skip(skip).limit(limit)
    stored_model = list(stored_model)
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
    return stored_model


@router.get('/find/cert/{id}', response_model=Terminal)
async def find_terminal_cert(
        id: str = Path(..., title='Query to transaction.',
                       regex='^(?![a-z])[a-z0-9]+$'),
        current_user: User = Depends(admin_via_find_intermediate)
):
    stored_model = await db.find_one(collection=COLLECTION, query={'_id': id})
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Not found item.')
    return stored_model


@router.post('/issue/cert', response_model=Terminal,
             status_code=status.HTTP_201_CREATED)
async def issue_terminal_cert(
        payload: Terminal = Depends(admin_via_create_terminal),
        current_user: User = Depends(get_signs_active_user)
):
    group_certificate = await db.find_one(
        collection='intermediates',
        query={
            '_id': payload.imd_detail.id,
            'channel_access_token': current_user.channel_access_token,
            'type': 'group'
        }
    )
    if not group_certificate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Your organization not create intermediate individual.'
        )
    if await db.find_one(collection='terminals', query={
        'imd_detail._id': group_certificate['_id'],
        'subject': payload.subject
    }):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Terminal cert is already exits.')
    profile = {
        'uid': current_user.uid,
        'username': current_user.username,
        'full_name': current_user.full_name,
        'email': current_user.email,
        'channel_access_token': current_user.channel_access_token
    }
    payload.imd_detail = group_certificate
    payload.owner = profile
    item_model = jsonable_encoder(payload)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return item_model


@router.put('/solve/cert/{id}', response_model=Terminal)
async def edit_terminal_cert(
        payload: UpdateTerminal,
        id: str = Path(..., title='Query to transaction.',
                       regex='^(?![a-z])[a-z0-9]+$'),
        current_user: User = Depends(admin_via_find_intermediate)
):
    item_model = jsonable_encoder(payload)
    query = {'_id': id}
    values = {'$set': item_model}
    if (await db.update_one(collection=COLLECTION,
                            query=query,
                            values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Not found {id} or update already exits.')
    return item_model


@router.delete('/purge/cert/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def purge_terminal_cert(
        id: str = Path(..., title='Query to transaction.',
                       regex='^(?![a-z])[a-z0-9]+$'),
        current_user: User = Depends(admin_via_find_intermediate)
):
    if (await db.delete_one(collection=COLLECTION, query={'_id': id})) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Intermediate cert is not found {id}."
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content={'status': 'success'})
