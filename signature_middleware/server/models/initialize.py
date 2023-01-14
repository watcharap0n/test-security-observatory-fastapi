import pytz
from secrets import token_urlsafe
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional, Union
from pydantic import BaseModel, Field, validator
from ..db import PyObjectId
from ..models.terminal import CertificateJDS


class Initialized(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    channel_access_token: str = Field(default_factory=token_urlsafe)
    organization: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9 ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    signs_quota: Optional[int] = 100
    cert_quota: Optional[int] = 100
    detail: CertificateJDS
    expiration_date: Union[datetime, str] = None
    expiration_date_cert: Optional[datetime] = None
    date: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'organization': 'Thaicom',
                'signs_quota': 100,
                'cert_quota': 100,
                'detail': {},
                'expiration_date': None
            }
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt

    @validator('expiration_date_cert', pre=True, always=True)
    def set_expire(cls, expiration_date_cert):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt + timedelta(days=365)


class UpdateInitialize(BaseModel):
    organization: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9 ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    signs_quota: Optional[int] = 100
    cert_quota: Optional[int] = 100
    expiration_date: Union[datetime, str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'organization': 'personal',
                'signs_quota': 100,
                'cert_quota': 99,
                'expiration_date': None
            }
        }
