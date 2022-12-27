import pytz
import time
import os
import logging
from datetime import datetime
from mangum import Mangum
from collections import OrderedDict
from fastapi import FastAPI, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi.responses import JSONResponse
from starlette.responses import Response
from .authentication import authenticate
from .routes import initialize, intermediate, terminal
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

origins = [
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080"
]

CSP: dict[str, str | list[str]] = {
    "default-src": "'self'",
    "img-src": [
        "*",
        # For SWAGGER UI
        "data:",
    ],
    "connect-src": "'self'",
    "script-src": "'self'",
    "style-src": ["'self'", "'unsafe-inline'"],
    "script-src-elem": [
        # For SWAGGER UI
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        "'sha256-1I8qOd6RIfaPInCv8Ivv4j+J0C6d7I8+th40S5U/TVc='",
    ],
    "style-src-elem": [
        # For SWAGGER UI
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    ],
}


def parse_policy(policy: dict[str, str | list[str]] | str) -> str:
    """Parse a given policy dict to string."""
    if isinstance(policy, str):
        # parse the string into a policy dict
        policy_string = policy
        policy = OrderedDict()

        for policy_part in policy_string.split(";"):
            policy_parts = policy_part.strip().split(" ")
            policy[policy_parts[0]] = " ".join(policy_parts[1:])

    policies = []
    for section, content in policy.items():
        if not isinstance(content, str):
            content = " ".join(content)
        policy_part = f"{section} {content}"

        policies.append(policy_part)

    parsed_policy = "; ".join(policies)

    return parsed_policy


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    def __init__(self, app: FastAPI, csp: bool = True) -> None:
        """Init SecurityHeadersMiddleware.

        :param app: FastAPI instance
        :param no_csp: If no CSP should be used;
            defaults to :py:obj:`False`
        """
        super().__init__(app)
        self.csp = csp

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Dispatch of the middleware.

        :param request: Incoming request
        :param call_next: Function to process the request
        :return: Return response coming from processed request
        """
        headers = {
            "Content-Security-Policy": "" if not self.csp else parse_policy(CSP),
            "Cross-Origin-Opener-Policy": "same-origin",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Strict-Transport-Security": "max-age=31556926; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }
        response = await call_next(request)
        response.headers.update(headers)
        return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    authenticate,
    prefix='/jwt/auth',
    tags=['JWT']
)

app.include_router(
    initialize.router,
    prefix='/initial',
    tags=['Initialized']
)

app.include_router(
    intermediate.router,
    prefix='/intermediate',
    tags=['Intermediate']
)

app.include_router(
    terminal.router,
    prefix='/terminal',
    tags=['Terminal']
)

app.include_router(
    apply.router,
    prefix='/jwt/auth',
    tags=['CSRF'],
)

log = logging.getLogger("uvicorn")
handler = Mangum(app)

description = """
SIGNATURE SERVICE. 👋🏻

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
        title="SIGNATURE SERVICE",
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
    response.headers["X-Process-Time"] = str(process_time)
    pass_url = str(request.url)
    sentence = '../../' or '..%2F..%2F' or '/../../'
    if sentence in pass_url:
        return RedirectResponse(status_code=status.HTTP_303_SEE_OTHER, url='/404')
    return response


@app.on_event("startup")
async def startup_event():
    """Start up event for FastAPI application."""
    log.info("Starting up server signature")
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
        Application shutdown server signature
        """
        create_log.write(txt)
    log.info("Shutting down...")


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': 'Missing Cookie csrf-token'}
    )
