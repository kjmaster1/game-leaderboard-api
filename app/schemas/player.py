from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional

class PlayerRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 30:
            raise ValueError('Username must be 30 characters or fewer')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens and underscores')
        return v

    @field_validator('password')
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

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