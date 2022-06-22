from typing import List

from aiocache.factory import Cache, CacheHandler
from fastapi import FastAPI, Form, UploadFile, File, Response, Request
from fastapi import BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from cache import clear_caches, close_caches, use_caches, get_settings
from exceptions import credentials_exception, form_exception
from exceptions import unauthorized_exception
from mail import Mail
from models.token import TokenData
from settings import Settings
from util.date import get_current_time
from util.random_string import get_random_string
from util.tasks import remove_entries
from validation import validate_email
from util.authentication.token import check_token, set_new_tokens


app = FastAPI(docs_url=get_settings().DOCS_URL, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().ORIGINS,
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    settings = get_settings()
    await clear_caches(settings)


@app.on_event("shutdown")
async def shutdown():
    settings = get_settings()
    await close_caches(settings)


@app.post('/api/v1/send')
async def send_authenticated(
    request: Request,
    background_tasks: BackgroundTasks,
    recipients: List[str] = Form(...),
    subject: str = Form(...),
    html: str = Form(None),
    plaintext: str = Form(None),
    files:  List[UploadFile] = File(None),
    caches: CacheHandler = Depends(use_caches),
    settings: Settings = Depends(get_settings),
    token_data: TokenData = Depends(check_token)
):
    # Compare request ip to token ip
    ip = request.client.host
    if ip != token_data.ip:
        raise credentials_exception("not valid ip")

    # Make some validations
    for recipient in recipients:
        if not validate_email(recipient):
            raise form_exception(f"Invalid recipient: {recipient}")

    # Connect to cache
    ip_cache: Cache.REDIS = caches.get(settings.REQUESTS_IP_CACHE)
    sid_cache: Cache.REDIS = caches.get(settings.REQUESTS_SID_CACHE)

    # Check if the user recently sent any requests
    ip_check = await ip_cache.get(token_data.ip)
    sid_check = await sid_cache.get(token_data.uid)

    if ip_check or sid_check:
        raise unauthorized_exception()

    # Store request data to set the temporary restrictions to access the API
    await ip_cache.set(token_data.ip, get_current_time())
    await sid_cache.set(token_data.uid, get_current_time())

    # Remove restrictions after 60 seconds
    background_tasks.add_task(
        remove_entries, token_data.ip, token_data.uid, ip_cache, sid_cache)

    user, password = settings.MAIL_USERS[token_data.service]
    recipients = [settings.MAIL_TO[token_data.service]] + recipients
    # Prepare the mail client
    client = Mail(user, recipients, subject, files)
    await client.send_email(password, plaintext, html)

    return JSONResponse({"status": "sent"})


@app.post('/api/v1/token')
def get_token(
    response: Response,
    request: Request,
    authentication: OAuth2PasswordRequestForm = Depends(),
    settings: Settings = Depends(get_settings),
):
    # Check the service authentication credentials
    try:
        if authentication.password != settings.SERVICES_KEYS[authentication.username]:  # noqa: E501
            raise credentials_exception()
    except KeyError:
        raise credentials_exception()
    uid = get_random_string(32)
    ip = request.client.host
    access_token = set_new_tokens(
        uid, settings, response, ip, authentication.username)

    return {settings.ACCESS_TOKEN_NAME: access_token,
            "access_token": access_token,
            "token_type": "bearer",
            "maxAge": settings.ACCESS_COOKIE_EXPIRE_TIME}
