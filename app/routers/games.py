from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.game import Game
from app.models.player import Player
from app.schemas.game import GameCreate, GameUpdate, GameResponse
from app.auth import get_current_player, get_admin_player

router = APIRouter(prefix="/games", tags=["Games"])

@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(
    payload: GameCreate,
    db: Session = Depends(get_db),
    admin: Player = Depends(get_admin_player)
):
    existing = db.query(Game).filter(Game.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A game with this name already exists"
        )
    game = Game(**payload.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

@router.get("/", response_model=List[GameResponse])
def list_games(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Game)
    if active_only:
        query = query.filter(Game.is_active == True)
    return query.order_by(Game.name).all()

@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return game

@router.patch("/{game_id}", response_model=GameResponse)
def update_game(
    game_id: str,
    payload: GameUpdate,
    db: Session = Depends(get_db),
    admin: Player = Depends(get_admin_player)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(game, field, value)
    db.commit()
    db.refresh(game)
    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: str,
    db: Session = Depends(get_db),
    admin: Player = Depends(get_admin_player)
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    db.delete(game)
    db.commit()