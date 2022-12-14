from bson import ObjectId
from ..db import PyObjectId
from typing import Optional, Union, List
from pydantic import BaseModel, Field


class CertificateJDS(BaseModel):
    signerProfileName: Optional[str] = Field(
        'yourSign_test_itmd',
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9_]+$',
        description='Allow only alphabetic eng character & number endswith.'
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
    name: str
    available_people: Union[List, None] = []
    detail: CertificateJDS


class Terminal(BaseModel):
    name: Union[str, None] = None
    owner: str
    certs: Union[List, None] = []


class Intermediate(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    type: str
    name: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9 ]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    terminal: Union[List, None] = []

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


class Initialized(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    company_name: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z0-9]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    quota: Optional[int] = 100
    remain_quota: Optional[int] = 100
    intermediate: Union[List, None] = []

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'company_name': 'Thaicom',
                'quota': 100,
                'remain_quota': 100,
                'intermediate': []
            }
        }


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
