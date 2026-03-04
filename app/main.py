from fastapi import FastAPI
from app.database import engine, Base
from app.routers import players, games, matches, leaderboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Game Leaderboard API",
    description="A REST API for tracking players, matches, and leaderboards across multiple games.",
    version="1.0.0",
)

app.include_router(players.router)
app.include_router(games.router)
app.include_router(matches.router)
app.include_router(leaderboard.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}