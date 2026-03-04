from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.match import Match, MatchPlayer, MatchStatus
from app.models.game import Game
from app.models.player import Player
from app.schemas.match import MatchCreate, MatchResponse
from app.auth import get_current_player

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    payload: MatchCreate,
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    # Verify game exists and is active
    game = db.query(Game).filter(Game.id == payload.game_id, Game.is_active == True).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found or inactive"
        )

    # Verify all players exist
    player_ids = [r.player_id for r in payload.results]
    players = db.query(Player).filter(Player.id.in_(player_ids)).all()
    if len(players) != len(player_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more players not found"
        )

    # Create the match
    match = Match(
        game_id=payload.game_id,
        status=MatchStatus.completed,
        played_at=payload.played_at,
    )
    db.add(match)
    db.flush()

    # Add player results
    for result in payload.results:
        match_player = MatchPlayer(
            match_id=match.id,
            player_id=result.player_id,
            score=result.score,
            placement=result.placement,
        )
        db.add(match_player)

    db.commit()
    db.refresh(match)
    return match

@router.get("/", response_model=List[MatchResponse])
def list_matches(
    game_id: Optional[str] = None,
    player_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    query = db.query(Match)
    if game_id:
        query = query.filter(Match.game_id == game_id)
    if player_id:
        query = query.join(Match.match_players).filter(MatchPlayer.player_id == player_id)
    return query.order_by(Match.created_at.desc()).offset(offset).limit(limit).all()

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: str,
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    return match

@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: str,
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    # Only the submitter or an admin can delete
    is_participant = any(mp.player_id == current_player.id for mp in match.match_players)
    if not is_participant and not current_player.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete matches you participated in"
        )
    db.delete(match)
    db.commit()