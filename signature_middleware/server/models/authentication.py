from uuid import uuid4
import pytz
from bson import ObjectId
from datetime import datetime
from typing import Union, List, Optional
from pydantic import BaseModel, Field, validator, EmailStr, UUID4
from fastapi_csrf_protect import CsrfProtect
from ..db import PyObjectId


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


class User(BaseModel):
    uid: str
    username: str
    role: str
    channel_access_token: Union[str, None] = None
    email: Union[EmailStr, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    date: datetime


class TableUser(BaseModel):
    uid: str
    username: str
    role: str
    channel_access_token: Union[str, None] = None
    email: Union[EmailStr, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    expiration_date: Optional[datetime] = None
    date: datetime


class UserInDB(User):
    hashed_password: str


class Register(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    uid: UUID4 = Field(default_factory=uuid4)
    username: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-z0-9_]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    hashed_password: str
    email: Union[EmailStr, None] = None
    full_name: Union[str, None] = Field(
        None,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z ]+$',
        description='Allow only alphabetic eng character'
    )
    expiration_date: Optional[datetime] = None
    channel_access_token: Union[str, None] = None
    role: Optional[str] = 'Member'
    disabled: Optional[bool] = False
    date: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}
        validate_assignment = True
        schema_extra = {
            'example': {
                'username': 'kane',
                'hashed_password': 'secret',
                'email': 'wera.watcharapon@gmail.com',
                'full_name': 'watcharapon weeraborirak',
                'channel_access_token': '',
                'cert': {}
            }
        }

    @validator('date', pre=True, always=True)
    def set_name(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class UpdateMember(BaseModel):
    email: Union[EmailStr, None] = None
    full_name: Union[str, None] = Field(
        None,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z ]+$',
        description='Allow only alphabetic eng character'
    )
    role: Optional[str] = 'Member'
    disabled: Optional[bool] = False
    channel_access_token: Union[str, None] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            'example': {
                'email': 'exkasan@gmail.com',
                'full_name': 'watcharapon weeraborirak',
                'channel_access_token': ''
            }
        }


class CsrfSettings(BaseModel):
    secret_key: str = 'thaicominnovationdigitaltransformation'


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
