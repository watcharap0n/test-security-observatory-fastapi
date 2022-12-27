import pytz
from bson import ObjectId
from datetime import datetime
from typing import Union, Optional, List
from pydantic import BaseModel, Field, validator
from ..db import PyObjectId
from ..models.terminal import CertificateJDS


class Intermediate(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    type: Optional[str] = None
    subject: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9 ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    disabled: Union[bool, None] = True
    detail: CertificateJDS
    date: Optional[datetime] = None
    channel_access_token: Union[str, None] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'type': 'group',
                'subject': 'Intermediate Department',
                'detail': {},
                'channel_access_token': ''
            }
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class ChannelAccess(Intermediate):
    channel_access_token: Optional[str] = None


class UpdateIntermediate(BaseModel):
    subject: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9 ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'subject': 'HR Department',
            }
        }
