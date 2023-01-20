import pytz
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Union, Optional, List
from pydantic import BaseModel, Field, validator, EmailStr
from ..db import PyObjectId


class CertificateJDS(BaseModel):
    signerProfileName: Optional[str] = Field(
        'yourSign_test_itmd',
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_]+$',
        description='Allow only alphabetic eng character & number endswith.',
    )
    signerPassword: Optional[str] = 'P@ssw0rd'
    signerPurpose: Optional[str] = 'GENERAL'
    profileName: Optional[str] = Field(
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_]+$',
        description='Allow only alphabetic eng character & number endswith.',
    )
    password: Optional[str] = None
    commonName: Optional[str] = None
    orgUnit: Optional[str] = None
    org: Optional[str] = None
    locality: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    validityDays: Optional[int] = 365
    reqRefNo: Union[int, None] = None

    class Config:
        validate_assigment = True
        schema_extra = {
            'example': {
                'signerProfileName': 'yourSign_test_itmd',
                'signerPassword': 'P@ssw0rd',
                'signerPurpose': 'GENERAL',
                'profileName': 'Arak',
                'password': 'secret',
                'commonName': 'demo signs',
                'orgUnit': 'Graduate Studies',
                'org': 'Vidyasirimedhi Institute of Science and Technology',
                'locality': 'Wangchan',
                'state': 'Rayoug',
                'country': 'TH',
                'validityDays': 730
            }
        }

    @validator('reqRefNo', pre=True, always=True)
    def set_ts(cls, reqRefNo):
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        return ts


class AvailablePeople(BaseModel):
    uid: Union[str, None] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Union[EmailStr, None] = 'sample@gmail.comn'
    disabled: Optional[bool] = False
    date: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assigment = True
        schema_extra = {
            'uid': '1234567890112233',
            'username': 'kane',
            'full_name': 'watcharapon weeraborirak',
            'email': 'sample@gmail.com'
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class Profile(BaseModel):
    uid: Union[str, None] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Union[EmailStr, None] = 'sample@gmail.comn'
    channel_access_token: Optional[str] = None
    date: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assigment = True
        schema_extra = {
            'example': {
                'uid': '1234567890112233',
                'username': 'kane',
                'full_name': 'watcharapon weeraborirak',
                'email': 'sample@gmail.com'
            }
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class ImdDetail(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    type: Union[str, None] = None
    subject: Optional[str] = None
    channel_access_token: Optional[str] = None


class Terminal(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    imd_detail: Union[ImdDetail, None] = None
    subject: Union[str, None] = Field(
        None,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_ ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    owner: Union[Profile, None] = None
    available_people: Union[List[AvailablePeople], None] = []
    detail: Union[CertificateJDS, None] = None
    expiration_date: Union[datetime, str] = None
    disabled: Union[bool, None] = False
    date: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'imd_detail': {},
                'subject': 'Department HR',
                'available_people': [],
                'detail': {}
            }
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class UpdateTerminal(BaseModel):
    subject: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_ ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    available_people: Union[List, None] = []
    detail: CertificateJDS

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'subject': 'Department HR',
                'available_people': [],
                'detail': {}
            }
        }
