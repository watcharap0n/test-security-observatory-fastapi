import pytz
from bson import ObjectId
from datetime import datetime
from typing import Union, Optional, List
from pydantic import BaseModel, Field, validator
from ..db import PyObjectId


class CertificateJDS(BaseModel):
    signerProfileName: Optional[str] = Field(
        'yourSign_test_itmd',
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_]+$',
        description='Allow only alphabetic eng character & number endswith.',
    )
    signerPassword: Optional[str] = 'P@ssw0rd'
    signerPurpose: Optional[str] = 'GENERAL'
    profileName: str
    password: str
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


class Profile(BaseModel):
    uid: str
    name: str
    date: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assigment = True
        schema_extra = {
            'example': {
                'uid': '1234567890112233',
                'name': 'watcharapon'
            }
        }

    @validator('date', pre=True, always=True)
    def set_date(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class Terminal(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    name: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_ ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    owner: Profile
    available_people: Union[List, None] = []
    detail: CertificateJDS

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'name': 'Department HR',
                'owner': 'watcharapon',
                'available_people': [],
                'detail': {}
            }
        }
