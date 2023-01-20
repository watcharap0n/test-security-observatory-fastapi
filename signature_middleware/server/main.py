import pytz
import time
import os
import logging
from aioredis import Redis
from datetime import datetime
from mangum import Mangum
from fastapi import FastAPI, status, Request, Depends
from fastapi_limiter import FastAPILimiter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from .authentication import authenticate
from .routes import initialize
from .dependencies.policy import SecurityHeadersMiddleware
from .dependencies.router import apply

app = FastAPI(
    version=os.environ.get('SERVER_VERSION', '1.0.9'),
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
    include_in_schema=os.getenv('OPENAPI_SCHEMA', True),
)

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, 'static/')
os.makedirs(st_abs_file_path, exist_ok=True)
app.mount('/static', StaticFiles(directory=st_abs_file_path), name='static')

RATE_PER_TIME = int(os.getenv('RATE_PER_TIME', 3))
RATE_AWAIT = int(os.getenv('RATE_AWAIT', 5))

app.add_middleware(
    SecurityHeadersMiddleware,
    csp=True
)

app.include_router(
    authenticate,
    prefix='/jwt/auth',
    tags=['JWT'],
    dependencies=[Depends(RateLimiter(
        times=RATE_PER_TIME,
        seconds=RATE_AWAIT
    ))]
)

app.include_router(
    initialize.router,
    prefix='/initial',
    tags=['Initialized'],
    dependencies=[Depends(RateLimiter(
        times=RATE_PER_TIME,
        seconds=RATE_AWAIT
    ))]
)

app.include_router(
    apply.router,
    prefix='/jwt/auth',
    tags=['CSRF'],
    dependencies=[Depends(RateLimiter(
        times=RATE_PER_TIME,
        seconds=RATE_AWAIT
    ))]
)

log = logging.getLogger("uvicorn")
handler = Mangum(app)

description = """
SERVICE SECURE SAMPLE. 👋🏻

## APIs

You can **read items each API**.

You will be able to:

***prefix /***
"""


@app.get('/404', response_class=HTMLResponse)
async def not_found_404():
    return """
        <html>
            <head>
                <title> Not found in here </title>
            <head>
            <body>
                <h1> Not found page </h1>
            </body>
        </html>
        """


def customer_openapi_signature():
    """
    docs description API
    :return:
        -> func
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SERVICE SECURE SAMPLE.",
        version="1.0.9",
        description=description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = customer_openapi_signature


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    process_time = '{:2f}'.format(process_time)
    response.headers['X-Process-Time'] = str(process_time)
    pass_url = str(request.url)
    sentence = '../../' or '..%2F..%2F' or '/../../'
    if sentence in pass_url:
        return RedirectResponse(status_code=status.HTTP_303_SEE_OTHER, url='/404')
    return response


@app.on_event("startup")
async def startup_event():
    """Start up event for FastAPI application."""
    r = Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0
    )
    log.info(r)
    await FastAPILimiter.init(r)

    log.info("Starting up service")
    root_dir = os.path.dirname(__file__)
    static_dir = os.path.join(root_dir, 'static')
    log_dir = os.path.join(static_dir, 'log')
    os.makedirs(log_dir, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event for FastAPI application."""
    tz = pytz.timezone('Asia/Bangkok')
    dt = datetime.now(tz)
    timestamp = datetime.timestamp(dt)
    with open(f'{st_abs_file_path}/log/shutdown_event.txt', mode="w") as create_log:
        txt = f"""
        time: {dt} | timezone - asia/bangkok
        timestamp: {timestamp}
        Application shutdown service
        """
        create_log.write(txt)
    log.info("Shutting down...")


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': 'Missing Cookie csrf-token'}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )
