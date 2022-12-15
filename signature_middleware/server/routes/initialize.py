from typing import List, Union
from fastapi import APIRouter, Query, Path, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from ..db import db
from ..models.authentication import User
from ..models.initialize import Initialized, UpdateInitialize
from ..dependencies.router.evaluate import evaluate_duplication_company_name, \
    permission_super_admin_via_find

router = APIRouter()

COLLECTION = 'certificates'


@router.get('/find/company', response_model=List[Initialized])
async def find_root(
        skip: Union[int, None] = Query(default=0,
                                       title='Skip or start documents in collection'),
        limit: Union[int, None] = Query(default=10,
                                        title='Limit or end documents in collection'),
        current_user: User = Depends(permission_super_admin_via_find)
):
    stored_model = await db.find(collection=COLLECTION, query={})
    stored_model = stored_model.skip(skip).limit(limit)
    stored_model = list(stored_model)
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
    return stored_model


@router.get('/find/company/{id}', response_model=Initialized)
async def find_root_one(
        id: str = Path(title='Document ID in collection for get item.'),
        current_user: User = Depends(permission_super_admin_via_find)
):
    stored_model = await db.find_one(collection=COLLECTION, query={'_id': id})
    if not stored_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found item.')
    return stored_model


@router.post('/issue/company', response_model=Initialized)
async def create_root(
        payload: Initialized = Depends(evaluate_duplication_company_name),
):
    item_model = jsonable_encoder(payload)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return payload


@router.put('/solve/company/{id}', response_model=UpdateInitialize)
async def update_root(
        id: str,
        payload: Initialized = Depends(evaluate_duplication_company_name),
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
