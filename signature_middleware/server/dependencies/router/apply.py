import os
from typing import Union
from fastapi import APIRouter, Depends, status, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect

router = APIRouter()


async def before_access_csrf(csrf_header: Union[str, None] = Header(default=None)):
    if not csrf_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='CSRF HEADER is bad request.')
    if csrf_header != os.getenv('CSRF_HEADER', None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='CSRF HEADER header invalid')


@router.get('/csrftoken', summary='Cross site request forgery token.')
async def get_csrf_token(
        before_access=Depends(before_access_csrf),
        csrf_protect: CsrfProtect = Depends()
):
    """
    :param before_access:
    :param csrf_protect\n
        - **fastapi_csrf_protect module using cookie authentication**
        - response to cookie | {csrf_token: cookie}
    """
    response = JSONResponse(status_code=status.HTTP_200_OK, content={'csrf_token': 'cookie'})
    csrf_protect.set_csrf_cookie(response)
    return response
