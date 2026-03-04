from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GameCreate(BaseModel):
    name: str
    description: Optional[str] = None
    max_players: Optional[str] = None

class GameUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_players: Optional[str] = None
    is_active: Optional[bool] = None

class GameResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    max_players: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}