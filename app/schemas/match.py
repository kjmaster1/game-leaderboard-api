from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.match import MatchStatus
from pydantic import field_validator

class MatchPlayerResult(BaseModel):
    player_id: str
    score: int
    placement: Optional[int] = None

    @field_validator('score')
    @classmethod
    def score_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Score cannot be negative')
        return v

    @field_validator('placement')
    @classmethod
    def placement_valid(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError('Placement must be 1 or higher')
        return v

class MatchCreate(BaseModel):
    game_id: str
    played_at: Optional[datetime] = None
    results: List[MatchPlayerResult]

class MatchPlayerResponse(BaseModel):
    player_id: str
    score: int
    placement: Optional[int] = None

    model_config = {"from_attributes": True}

class MatchResponse(BaseModel):
    id: str
    game_id: str
    status: MatchStatus
    played_at: Optional[datetime] = None
    created_at: datetime
    match_players: List[MatchPlayerResponse]

    model_config = {"from_attributes": True}