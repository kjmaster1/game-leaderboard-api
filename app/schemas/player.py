from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class PlayerRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class PlayerLogin(BaseModel):
    username: str
    password: str

class PlayerResponse(BaseModel):
    id: str
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class PlayerPublic(BaseModel):
    id: str
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    player_id: Optional[str] = None