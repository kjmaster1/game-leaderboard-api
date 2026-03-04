from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from typing import List, Optional
from app.database import get_db
from app.models.match import Match, MatchPlayer, MatchStatus
from app.models.game import Game
from app.models.player import Player
from pydantic import BaseModel

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

class LeaderboardEntry(BaseModel):
    rank: int
    player_id: str
    username: str
    matches_played: int
    total_score: int
    average_score: float
    wins: int

    model_config = {"from_attributes": True}

class LeaderboardResponse(BaseModel):
    game_id: str
    game_name: str
    entries: List[LeaderboardEntry]

@router.get("/{game_id}", response_model=LeaderboardResponse)
def get_leaderboard(
    game_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    # Aggregate stats per player for this game
    results = (
        db.query(
            Player.id.label("player_id"),
            Player.username.label("username"),
            func.count(MatchPlayer.id).label("matches_played"),
            func.sum(MatchPlayer.score).label("total_score"),
            func.avg(MatchPlayer.score).label("average_score"),
            func.sum(
                (MatchPlayer.placement == 1).cast(Integer)
            ).label("wins"),
        )
        .join(MatchPlayer, Player.id == MatchPlayer.player_id)
        .join(Match, MatchPlayer.match_id == Match.id)
        .filter(Match.game_id == game_id)
        .filter(Match.status == MatchStatus.completed)
        .group_by(Player.id, Player.username)
        .order_by(func.sum(MatchPlayer.score).desc())
        .limit(limit)
        .all()
    )

    entries = [
        LeaderboardEntry(
            rank=index + 1,
            player_id=row.player_id,
            username=row.username,
            matches_played=row.matches_played,
            total_score=int(row.total_score or 0),
            average_score=round(float(row.average_score or 0), 2),
            wins=int(row.wins or 0),
        )
        for index, row in enumerate(results)
    ]

    return LeaderboardResponse(game_id=game_id, game_name=game.name, entries=entries)

@router.get("/{game_id}/player/{player_id}", response_model=LeaderboardEntry)
def get_player_stats(
    game_id: str,
    player_id: str,
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    result = (
        db.query(
            Player.id.label("player_id"),
            Player.username.label("username"),
            func.count(MatchPlayer.id).label("matches_played"),
            func.sum(MatchPlayer.score).label("total_score"),
            func.avg(MatchPlayer.score).label("average_score"),
            func.sum(
                (MatchPlayer.placement == 1).cast(Integer)
            ).label("wins"),
        )
        .join(MatchPlayer, Player.id == MatchPlayer.player_id)
        .join(Match, MatchPlayer.match_id == Match.id)
        .filter(Match.game_id == game_id)
        .filter(Match.status == MatchStatus.completed)
        .filter(Player.id == player_id)
        .group_by(Player.id, Player.username)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stats found for this player in this game"
        )

    return LeaderboardEntry(
        rank=0,
        player_id=result.player_id,
        username=result.username,
        matches_played=result.matches_played,
        total_score=int(result.total_score or 0),
        average_score=round(float(result.average_score or 0), 2),
        wins=int(result.wins or 0),
    )