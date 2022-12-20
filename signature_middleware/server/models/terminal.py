import pytz
from bson import ObjectId
from datetime import datetime
from typing import Union, Optional, List, Dict
from pydantic import BaseModel, Field, validator, EmailStr, UUID4
from ..db import PyObjectId


class CertificateJDS(BaseModel):
    signerProfileName: Optional[str] = Field(
        'yourSign_test_itmd',
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_]+$',
        description='Allow only alphabetic eng character & number endswith.',
    )
    signerPassword: Optional[str] = 'P@ssw0rd'
    signerPurpose: Optional[str] = 'GENERAL'
    profileName: Optional[str] = 'Test JDS'
    password: Optional[str] = 'secret'
    commonName: Optional[str] = 'demo signs'
    orgUnit: Optional[str] = 'Graduate Studies'
    org: Optional[str] = 'Vidyasirimedhi Institute of Science and Technology'
    locality: Optional[str] = 'Wangchan'
    state: Optional[str] = 'Rayoug'
    country: Optional[str] = 'TH'
    validityDays: Optional[int] = 730
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


class AvailablePeople(BaseModel):
    uid: Union[str, None] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Union[EmailStr, None] = 'sample@gmail.comn'
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


class Terminal(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    token: str
    subject: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_ ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    owner: Union[Profile, None] = None
    available_people: Union[List[AvailablePeople], None] = []
    detail: CertificateJDS

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'token': '',
                'subject': 'Department HR',
                'available_people': [],
                'detail': {}
            }
        }


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
