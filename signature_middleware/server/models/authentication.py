import pytz
from bson import ObjectId
from datetime import datetime
from typing import Union, List, Optional
from pydantic import BaseModel, Field, validator, EmailStr
from ..db import PyObjectId


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


class User(BaseModel):
    username: str
    role: str
    email: Union[EmailStr, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class Register(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    username: str = Field(
        ...,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-z0-9]+$',
        description='Allow only alphabetic eng character & number endswith.'
    )
    hashed_password: str
    email: Union[EmailStr, None] = None
    full_name: Union[str, None] = Field(
        None,
        regex='^(?![0-9._])(?!.*[._]$)(?!.*\d_)(?!.*_\d)[a-zA-Z ]+$',
        description='Allow only alphabetic eng character'
    )
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
                'full_name': 'watcharapon weeraborirak'
            }
        }

    @validator('date', pre=True, always=True)
    def set_name(cls, date):
        tz = pytz.timezone('Asia/Bangkok')
        dt = datetime.now(tz)
        return dt


class UserInDB(User):
    hashed_password: str
