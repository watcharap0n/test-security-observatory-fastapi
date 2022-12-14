from typing import List, Union, Any
from fastapi import APIRouter, Query, Path, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from ..authentication import get_signs_active_user
from ..db import db
from ..models.authentication import User
from ..models.initialize import (Initialized, Intermediate, Terminal, Profile,
                                 CertificateJDS, UpdateIntermediate)

router = APIRouter()

COLLECTION = 'certificates'


async def evaluate_duplication_company_name(payload: Initialized):
    if await db.find_one(collection=COLLECTION, query={'company_name': payload.company_name}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Company name is duplicate.')
    return payload


@router.get('/find/root', response_model=List[Initialized])
async def find_root(
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start documents in collection'),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end documents in collection'),
        current_user: User = Depends(get_signs_active_user)
):
    stored_model = await db.find(collection=COLLECTION, query={})
    stored_model = stored_model.skip(skip).limit(limit)
    stored_model = list(stored_model)
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
    return stored_model


@router.get('/find/root/{id}', response_model=Initialized)
async def find_root_one(
        id: str = Path(title='Document ID in collection for get item.'),
        current_user: User = Depends(get_signs_active_user)
):
    stored_model = await db.find_one(collection=COLLECTION, query={'_id': id})
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
    return stored_model


@router.post('/create/root', response_model=Initialized)
async def create_root(
        payload: Initialized = Depends(evaluate_duplication_company_name),
        current_user: User = Depends(get_signs_active_user)
):
    item_model = jsonable_encoder(payload)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return payload


@router.put('/create/intermediate/{id}', response_model=Initialized)
async def create_intermediate(
        payload: Intermediate,
        id: str = Path('Is push to transaction group or personal.'),
        current_user: User = Depends(get_signs_active_user)
):
    item_model = jsonable_encoder(payload)
    query = {'_id': id}
    values = {'$push': {'intermediate': item_model}}
    if (await db.update_one(collection=COLLECTION, query=query, values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Already to update exits.')
    return await db.find_one(collection=COLLECTION, query=query)


@router.put('/update/intermediate/{id}', response_model=Initialized)
async def update_intermediate(
        payload: UpdateIntermediate,
        id: str = Path('Query to transaction.'),
        current_user: User = Depends(get_signs_active_user)
):
    item_model = jsonable_encoder(payload)
    query_intermediate = {'intermediate._id': id}
    values = {'$set': {'intermediate.$': item_model}}
    if (await db.update_one(collection=COLLECTION,
                            query=query_intermediate,
                            values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Not found {id} or update already exits.')
    stored_model = await db.find_one(collection=COLLECTION,
                                     query=query_intermediate)
    return stored_model


@router.post('/create/terminal')
async def create_cert(
        payload: Terminal,
        current_user: User = Depends(get_signs_active_user)
):
    pass


@router.post('/create/profile')
async def create_profile(
        payload: Profile,
        current_user: User = Depends(get_signs_active_user)
):
    pass


@router.post('/create/cert')
async def create_cert(
        payload: CertificateJDS,
        current_user: User = Depends(get_signs_active_user)
):
    pass
