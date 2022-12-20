from secrets import token_urlsafe
import pytz
from datetime import datetime
from bson import ObjectId
from typing import Optional, Union, List
from pydantic import BaseModel, Field, validator
from ..db import PyObjectId
from ..models.intermediate import Intermediate


class Initialized(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    channel_access_token: str = Field(default_factory=token_urlsafe)
    organization: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9 ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    quota: Optional[int] = 100
    remain_quota: Optional[int] = 100
    date: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'organization': 'Thaicom',
                'quota': 100,
                'remain_quota': 100,
            }
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class UpdateInitialize(BaseModel):
    organization: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    quota: Optional[int] = 100
    remain_quota: Optional[int] = 100

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'organization': 'personal',
                'quota': 100,
                'remain_quota': 99,
            }
        }
