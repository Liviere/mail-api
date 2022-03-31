from pydantic import BaseModel
from typing import Optional


# Token Models
class Token(BaseModel):
    accessToken: str
    tokenType: str


class TokenData(BaseModel):
    uid: Optional[str] = None
    ip: str
    service: str
