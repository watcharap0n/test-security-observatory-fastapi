from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, \
    Path
from fastapi.encoders import jsonable_encoder
from ..models.initialize import Initialized
from ..models.terminal import Terminal, Profile, UpdateTerminal
from ..models.authentication import User
from ..authentication import get_signs_active_user
from ..db import db

router = APIRouter()

COLLECTION = 'terminals'

async def check_duplicate_available(profile):
    await db.find_one(collection=COLLECTION, query={''})

@router.post('/issue/cert', response_model=Terminal)
async def issue_terminal_cert(
        payload: Terminal,
        current_user: User = Depends(get_signs_active_user)
):
    profile = {
        'uid': current_user.uid,
        'username': current_user.username,
        'full_name': current_user.full_name,
        'email': current_user.email
    }
    payload.owner = profile
    payload.available_people = [profile]
    item_model = jsonable_encoder(payload)
    await db.insert_one(collection=COLLECTION, data=item_model)
    return item_model


@router.put('/solve/cert/{id}', response_model=Initialized)
async def edit_terminal_cert(
        payload: UpdateTerminal,
        id: str
):
    item_model = jsonable_encoder(payload)
    query = {'intermediate._id': id}
    values = {'$set': {'intermediate.$.terminal': item_model}}
    if (await db.update_one(collection=COLLECTION,
                            query=query,
                            values=values)) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Not found {id} or update already exits.')
    stored_model = await db.find_one(collection=COLLECTION,
                                     query={'intermediate._id': item_model.get('_id')})
    return stored_model
