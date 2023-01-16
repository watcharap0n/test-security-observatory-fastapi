import pytz
from datetime import datetime
from typing import Optional
from ...db import db


async def log_transaction(
        method: str,
        endpoint: str,
        from_cache: bool,
        payload: Optional[dict] = None,
        info_user: Optional[dict] = None
):
    tz = pytz.timezone('Asia/Bangkok')
    await db.insert_one(collection='logs', data={
        'method': method,
        'endpoint': endpoint,
        'from_cache': from_cache,
        'payload': payload,
        'info_user': info_user,
        'datetime': datetime.now(tz)
    })
