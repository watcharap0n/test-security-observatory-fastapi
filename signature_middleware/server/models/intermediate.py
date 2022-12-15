import pytz
from bson import ObjectId
from datetime import datetime
from typing import Union, Optional, List
from pydantic import BaseModel, Field, validator
from ..db import PyObjectId


class Intermediate(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    type: str
    name: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9 ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    terminal: Union[List, None] = []
    date: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'type': 'personal',
                'name': 'watcharapon',
                'terminal': []
            }
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class UpdateIntermediate(BaseModel):
    type: str
    name: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9 ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    terminal: Union[List, None] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'type': 'personal',
                'name': 'watcharapon weeraborirak',
                'terminal': []
            }
        }
