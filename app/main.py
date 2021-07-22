from typing import List

from aiocache.factory import Cache, CacheHandler
from fastapi import FastAPI, Form, UploadFile, File
from fastapi import BackgroundTasks, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from cache import use_caches, get_settings
from exceptions import credentials_exception, form_exception
from mail import Mail
from settings import Settings
from util.date import get_current_time
from util.tasks import remove_entries
from validation import validate_email


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().ORIGINS,
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown():
    print("Clearing Caches")
    caches = use_caches()
    await caches.close()


@app.post('/')
async def send(
    # data: FormData,
    background_tasks: BackgroundTasks,
    serviceName: str = Form(...),
    serviceKey: str = Form(...),
    user: str = Form(...),
    password: str = Form(...),
    recipients: List[str] = Form(...),
    subject: str = Form(...),
    ip: str = Form(...),
    sid: str = Form(...),
    html: str = Form(None),
    plaintext: str = Form(None),
    files:  List[UploadFile] = File(None),
    caches: CacheHandler = Depends(use_caches),
    settings: Settings = Depends(get_settings)
):
    # Make some validations
    if not validate_email(user):
        raise form_exception("Invalid user")
    for recipient in recipients:
        if not validate_email(recipient):
            raise form_exception(f"Invalid recipient: {recipient}")

    # Check the service authentication credentials
    try:
        if serviceKey != settings.SERVICES_KEYS[serviceName]:
            raise credentials_exception()
    except KeyError:
        raise credentials_exception()

    # Connect to cache
    ip_cache: Cache.REDIS = caches.get(settings.REQUESTS_IP_CACHE)
    sid_cache: Cache.REDIS = caches.get(settings.REQUESTS_SID_CACHE)

    # Check if the user recently sent any requests
    ip_check = await ip_cache.get(ip)
    sid_check = await sid_cache.get(sid)

    if ip_check or sid_check:
        return JSONResponse({"status": "canceled", "info": "too many request"})

    # Store request data to set the temporary restrictions to access the API
    await ip_cache.set(ip, get_current_time())
    await sid_cache.set(sid, get_current_time())

    # Remove restrictions after 60 seconds
    background_tasks.add_task(remove_entries, ip, sid, ip_cache, sid_cache)

    # Prepare the mail client
    client = Mail(user, recipients, subject, files)
    await client.send_email(password, plaintext, html)

    return JSONResponse({"status": "sent"})
