from datetime import datetime, timedelta
from typing import Optional

from fastapi import Response, Depends, Request
from fastapi.security import OAuth2PasswordBearer
import jwt

from cache import get_settings
from models.token import TokenData
from settings import Settings
from exceptions import credentials_exception

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/token")


def create_token(
    hash_key: str,
    algorithm: str,
    values: dict,
    expires_delta: Optional[timedelta] = None
):
    to_encode = values.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, hash_key, algorithm=algorithm)
    return encoded_jwt


def set_new_tokens(
    uid: str,
    settings: Settings,
    response: Response,
    ip: str,
    service_name: str,
):

    # set refresh token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_TIME)
    access_token = create_token(
        settings.TOKEN_HASH,
        settings.ALGORITHM,
        values={"sub": uid, "ip": ip, "service": service_name},
        expires_delta=access_token_expires
    )

    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        path='/',
        max_age=settings.ACCESS_COOKIE_EXPIRE_TIME,
        domain=settings.DOMAINS[service_name],
        httponly=True,
        secure=settings.PRODUCTION,
    )

    return access_token


def decode_token(token, key, algorithm, ip):
    try:
        payload = jwt.decode(
            token, key, algorithms=[algorithm])
        uid: str = payload.get("sub")
        if uid is None:
            return False
        tokenIP: str = payload.get("ip")
        if ip != tokenIP:
            return False
        token_data = TokenData(uid=uid, ip=ip, service=payload.get("service"))
        return token_data
    except jwt.PyJWTError as err:
        print(err)
        return False


def check_token(
    request: Request,
    settings: Settings = Depends(get_settings),
    access_token: str = Depends(oauth2_scheme)
):
    ip = request.client.host
    token_data = decode_token(
        access_token, settings.TOKEN_HASH, settings.ALGORITHM, ip)
    if not token_data:
        raise credentials_exception()
    return token_data


def remove_cookies(response: Response, settings: Settings):
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value='',
        path='/',
        max_age=0,
        domain=settings.COOKIES_DOMAIN,
        httponly=True,
        secure=settings.PRODUCTION,
    )
