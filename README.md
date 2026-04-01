# Aura — Gamified Habit Tracker

A game-like habit dashboard where you manage habits by categories, visualize progress through an animated "Aura" character, and receive AI-powered narration and quests from an "AI Master" mentor.

## Tech Stack

| Layer    | Technology                                                                  |
| -------- | --------------------------------------------------------------------------- |
| Backend  | Python 3.12+, FastAPI, SQLAlchemy (async), PostgreSQL, Alembic              |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, ShadcnUI, TanStack Router + Query, Zustand |
| AI       | AWS Bedrock (Claude)                                                        |
| Auth     | OAuth2 (GitHub), JWT                                                        |

## Getting Started

### Prerequisites

- Python 3.12+, [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- Docker (for PostgreSQL)

### Backend

```bash
cd backend
cp .env.example .env
docker compose up -d          # start PostgreSQL
uv sync                       # install dependencies
uv run alembic upgrade head   # run migrations
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # starts on http://localhost:5173
```

## Project Structure

```
backend/
  app/
    api/          # route handlers
    models/       # SQLAlchemy models
    schemas/      # Pydantic schemas
    services/     # business logic
    core/         # security, constants, exceptions
    integrations/ # AWS Bedrock client
  alembic/        # database migrations
  tests/

frontend/
  src/
    api/          # HTTP client
    components/   # UI components
    hooks/        # TanStack Query hooks
    pages/        # route pages
    stores/       # Zustand stores
    types/        # TypeScript interfaces
    lib/          # utilities, constants
```
