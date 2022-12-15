from fastapi import APIRouter, status, HTTPException, Path, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ..db import db
from ..models import intermediate, initialize
from ..dependencies.router.evaluate import evaluate_duplication_intermediate, \
    permission_super_admin_via_revoke, permission_super_admin_via_find

router = APIRouter()

COLLECTION = 'certificates'


@router.put('/issue/level/{id}', response_model=initialize.Initialized,
            status_code=status.HTTP_201_CREATED)
async def create_intermediate_level(
        payload: intermediate.Intermediate = Depends(evaluate_duplication_intermediate),
        id: str = Path('Is push to transaction group or personal.'),
):
    item_model = jsonable_encoder(payload)
    query = {'_id': id}
    values = {'$push': {'intermediate': item_model}}
    if (await db.update_one(collection=COLLECTION, query=query, values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Already to update exits.')
    return await db.find_one(collection=COLLECTION, query=query)


@router.put('/solve/level/{id}', response_model=initialize.Initialized)
async def edit_intermediate_level(
        payload: intermediate.Intermediate = Depends(evaluate_duplication_intermediate),
        id: str = Path('Query to transaction.'),
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
                                     query={'intermediate._id': item_model.get('_id')})
    return stored_model


@router.delete('/purge/level/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def revoke_intermediate_level(
        id: str = Depends(permission_super_admin_via_revoke)
):
    if (await db.delete_one(collection=COLLECTION, query={"_id": id})) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Intermediate cert is not found {id}."
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={'status': 'success'})
