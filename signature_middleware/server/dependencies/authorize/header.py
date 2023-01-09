import os
from typing import Union
from fastapi import Header, status, HTTPException


async def signature_jwt_header(jwt_header: Union[str, None] = Header(default=None)):
    print(jwt_header)
    if not jwt_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='JWT header is bad request.')
    if jwt_header != os.getenv('JWT_HEADER', None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='JWT header invalid')
