from pydantic import BaseModel
from typing import Optional


# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    uid: Optional[str] = None
    ip: str
