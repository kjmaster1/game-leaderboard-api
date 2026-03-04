from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.player import Player
from app.schemas.player import PlayerRegister, PlayerLogin, PlayerResponse, PlayerPublic, Token
from app.auth import hash_password, verify_password, create_access_token, get_current_player

router = APIRouter(prefix="/players", tags=["Players"])

@router.post("/register", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def register(payload: PlayerRegister, db: Session = Depends(get_db)):
    existing = db.query(Player).filter(
        (Player.username == payload.username) | (Player.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    player = Player(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

@router.post("/login", response_model=Token)
def login(payload: PlayerLogin, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == payload.username).first()
    if not player or not verify_password(payload.password, player.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(data={"sub": player.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=PlayerResponse)
def get_me(current_player: Player = Depends(get_current_player)):
    return current_player

@router.get("/{player_id}", response_model=PlayerPublic)
def get_player(player_id: str, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    return player

@router.post("/make-admin/{player_id}", response_model=PlayerResponse)
def make_admin(
    player_id: str,
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player)
):
    # Only allow if there are no admins yet, or if requester is already admin
    admin_exists = db.query(Player).filter(Player.is_admin == True).first()
    if admin_exists and not current_player.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    player.is_admin = True
    db.commit()
    db.refresh(player)
    return player