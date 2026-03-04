from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from app.routers import players, games, matches, leaderboard

app = FastAPI(
    title="Game Leaderboard API",
    description="A REST API for tracking players, matches, and leaderboards across multiple games.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(players.router)
app.include_router(games.router)
app.include_router(matches.router)
app.include_router(leaderboard.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}