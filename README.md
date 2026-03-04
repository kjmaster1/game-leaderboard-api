# Game Leaderboard API

A production-ready REST API for tracking players, matches, and leaderboards across multiple games. Built with Python and FastAPI, featuring JWT authentication, role-based access control, and auto-generated interactive documentation.

**[Live API](https://web-production-7e5d.up.railway.app)** · **[Interactive Docs](https://web-production-7e5d.up.railway.app/docs)**

---

## Overview

This API provides the complete backend for a competitive gaming leaderboard system. It supports multiple games, tracks match results, and computes player rankings based on aggregated match statistics. Any game can be tracked — from Minecraft minigames to Chess to custom tournament formats.

---

## Features

- **JWT Authentication** — secure token-based auth with configurable expiry
- **Role-based access control** — admin and player roles with protected endpoints
- **Player management** — registration, login, and public profiles
- **Game management** — full CRUD, admin-only write access
- **Match tracking** — submit results for multiple players in a single request
- **Leaderboards** — ranked player standings per game with wins, total score, and average score
- **Player stats** — per-player stats and full match history with pagination
- **Input validation** — Pydantic validators with descriptive error messages
- **Rate limiting** — abuse protection on authentication endpoints
- **Database migrations** — schema versioning with Alembic
- **Interactive docs** — auto-generated Swagger UI at `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python 3.13 |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT via python-jose |
| Validation | Pydantic v2 |
| Rate Limiting | SlowAPI |
| Deployment | Railway |

---

## API Reference

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/players/register` | None | Register a new player |
| POST | `/players/login` | None | Login and receive JWT token |

### Players
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/players/me` | Required | Get your own profile |
| GET | `/players/{id}` | None | Get a player's public profile |
| GET | `/players/{id}/matches` | Required | Get a player's match history |
| POST | `/players/make-admin/{id}` | Required | Promote a player to admin |

### Games
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/games/` | None | List all active games |
| GET | `/games/{id}` | None | Get a single game |
| POST | `/games/` | Admin | Create a game |
| PATCH | `/games/{id}` | Admin | Update a game |
| DELETE | `/games/{id}` | Admin | Delete a game |

### Matches
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/matches/` | Required | Submit a match result |
| GET | `/matches/` | Required | List matches (filterable by game or player) |
| GET | `/matches/{id}` | Required | Get a single match |
| DELETE | `/matches/{id}` | Required | Delete a match |

### Leaderboard
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/leaderboard/{game_id}` | None | Get ranked leaderboard for a game |
| GET | `/leaderboard/{game_id}/player/{player_id}` | None | Get a player's stats for a game |

---

## Data Model

```
Player
  id, username, email, hashed_password, is_admin, created_at

Game
  id, name, description, max_players, is_active, created_at

Match
  id, game_id, status, played_at, created_at

MatchPlayer (junction table)
  id, match_id, player_id, score, placement, created_at
```

The `MatchPlayer` table is a junction between `Match` and `Player` that also carries match-specific data (score and placement). This enables efficient leaderboard aggregation via SQL GROUP BY queries without denormalising the schema.

---

## Running Locally

### Prerequisites
- Python 3.13+
- A PostgreSQL database (Supabase free tier recommended)

### Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/YOUR_USERNAME/game-leaderboard-api.git
   cd game-leaderboard-api
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file:
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   Generate a secure secret key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

   API: `http://localhost:8000`
   Docs: `http://localhost:8000/docs`

---

## Authentication Flow

```
1. POST /players/register  →  create account
2. POST /players/login     →  receive JWT token
3. Add header: Authorization: Bearer <token>
4. Access protected endpoints
```

Tokens expire after 30 minutes by default (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

---

## Example: Submit a Match Result

```bash
curl -X POST https://web-production-7e5d.up.railway.app/matches/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "your_game_id",
    "played_at": "2026-03-04T12:00:00Z",
    "results": [
      {"player_id": "player_1_id", "score": 1000, "placement": 1},
      {"player_id": "player_2_id", "score": 750, "placement": 2}
    ]
  }'
```

---

## Deployment

Deployed on [Railway](https://railway.app) with a [Supabase](https://supabase.com) PostgreSQL database.

To deploy your own instance:

1. Fork the repo
2. Create a new Railway project from the GitHub repo
3. Add environment variables: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
4. Railway will detect the `Procfile` and deploy automatically

---

## Design Decisions

**Why FastAPI over Django/Flask?**
FastAPI provides automatic OpenAPI documentation, native Pydantic integration for request validation, and excellent performance. For a pure API project with no server-rendered templates, it's the most productive modern Python choice.

**Why SQLAlchemy over Django ORM?**
SQLAlchemy gives explicit control over queries, making it straightforward to write the aggregation queries needed for leaderboard ranking. The leaderboard endpoint uses a single GROUP BY query rather than multiple round trips.

**Why Alembic over auto-creating tables?**
`Base.metadata.create_all()` is convenient for development but can't handle schema changes safely in production. Alembic provides versioned, reversible migrations — the industry standard approach.

---

## Future Improvements

- **ELO rating system** — replace raw score ranking with a skill-based rating that accounts for opponent strength
- **Tournament brackets** — support structured single/double elimination tournaments
- **WebSocket live updates** — push leaderboard changes to connected clients in real time
- **Refresh tokens** — extend sessions without requiring re-login
- **API key authentication** — allow server-to-server integrations without user sessions

---

## Author

Built by **kjmaster1** as a portfolio project demonstrating Python backend development, REST API design, and database modelling.

[GitHub](https://github.com/kjmaster1) · [YouTube Dashboard Project](https://github.com/kjmaster1/youtube-dashboard)
