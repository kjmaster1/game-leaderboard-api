from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base

class MatchStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.pending)
    played_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    game = relationship("Game", back_populates="matches")
    match_players = relationship("MatchPlayer", back_populates="match")

class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String, ForeignKey("matches.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    score = Column(Integer, default=0)
    placement = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="match_players")
    player = relationship("Player", back_populates="match_players")