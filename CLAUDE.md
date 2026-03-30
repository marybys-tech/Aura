# Aura — Gamified Habit Tracker with AI Master

## Code Standards (MUST FOLLOW)

### General
- **Modular, clean code**: small focused files (<200 lines). One concern per file. If a file grows large, split it.
- **DRY / SOLID / KISS**: no copy-paste, no god-objects, simplest solution that works.
- **Reusable components**: extract shared logic into hooks (frontend) or services (backend). UI components should be composable and generic where sensible.
- **No dead code**: don't leave commented-out code, unused imports, or placeholder stubs that do nothing.

### Backend (Python / FastAPI)
- **Thin route handlers**: routes validate input and delegate to services. No business logic in route files.
- **Service layer**: all business logic lives in `app/services/`. Services receive a DB session, never create their own.
- **Type everything**: use Pydantic schemas for all request/response bodies. Use Python type hints everywhere.
- **OpenAPI documentation**: every endpoint must have a clear `summary`, `description`, and `response_model`. Use `tags` to group endpoints. The auto-generated docs at `/docs` should be self-explanatory.
- **Tests**: unit tests for pure business logic (stats engine, scoring). Integration tests for API endpoints (test full request→response cycle). Use pytest fixtures and factories. Aim for high coverage on services and routes.
- **Security**: parameterized queries only (via ORM), validate all input with Pydantic, enforce ownership checks on every resource access.

### Frontend (React / TypeScript)
- **Small components**: one component per file, max ~150 lines. Split layout, logic, and presentation.
- **Custom hooks**: extract data-fetching and mutations into `hooks/` using TanStack Query. Components should not call `api` directly.
- **Type safety**: define all API response shapes in `types/`. No `any`.
- **Reusable UI**: use ShadcnUI primitives, compose them into domain components in `components/`. Don't duplicate styling.
- **Tests**: test components with Vitest + RTL. Test hooks with MSW mocks. Focus on user-visible behavior, not implementation details.

---

## Context

Build a gamified habit-tracking dashboard from scratch. Users manage habits by categories, see progress visualized as an animated "Aura" character, and receive AI-powered narration and quests from an "AI Master" mentor. The project is greenfield (empty git repo).

---

## Polished Idea Summary

**Aura** is a game-like habit dashboard where users:
- Register via GitHub OAuth, see avatar in header with logout dropdown
- Add habits in 6 categories: **Intelligence**, **Stamina**, **Sociality**, **Creativity**, **Discipline**, **Wellness** — each with a distinct color
- Configure habit schedules: daily, specific weekdays, or multiple times per day
- On the main dashboard: switch between **Today / Week / Month** views, see habits as cards (only today's are actionable — complete/skip), view stats by category, see AI-generated quests, and watch the Aura visualization. Week and month views show a read-only calendar/grid of past and future habit statuses.
- **Aura** is a breathing, glowing particle effect whose colors reflect category scores. Completing a habit triggers a color flare; consecutive skips cause fading and slower breathing
- **AI Master** (Oogway-style mentor) narrates completions/skips with wise humor via a popup, and generates daily/weekly quests targeting weak categories

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy (async + asyncpg), Alembic, uv (package manager) |
| Frontend | React 18+ (Vite), TypeScript, ShadcnUI, TanStack Query, Zustand |
| Database | PostgreSQL |
| AI | AWS Bedrock (Claude Haiku for narrations, Opus available for complex generation) |
| Auth | OAuth2 (GitHub), JWT access/refresh tokens |
| Testing | pytest + pytest-asyncio + testcontainers (backend), Vitest + RTL + MSW (frontend) |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                   React SPA                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Dashboard │ │  Habits  │ │  Aura Canvas     │ │
│  │  Page     │ │  Page    │ │  (2D particles)  │ │
│  └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│       └─────────────┼────────────────┘           │
│              TanStack Query + Zustand             │
│                     │ HTTP (JWT)                  │
└─────────────────────┼───────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────┐
│              FastAPI  (api/v1)                    │
│  ┌───────┐ ┌────────┐ ┌──────┐ ┌────────────┐  │
│  │ Auth  │ │ Habits │ │Stats │ │  AI Master │  │
│  │Service│ │Service │ │Engine│ │  Service   │──┼──► AWS Bedrock
│  └───┬───┘ └───┬────┘ └──┬───┘ └────────────┘  │
│      └─────────┼─────────┘                       │
│           SQLAlchemy (async)                      │
│                │                                  │
└────────────────┼─────────────────────────────────┘
                 │
          ┌──────┴──────┐
          │  PostgreSQL  │
          └─────────────┘
```

---

## Database Schema

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| email | VARCHAR(320) | UNIQUE |
| display_name | VARCHAR(100) | |
| avatar_url | VARCHAR(2048) | from OAuth |
| oauth_provider | VARCHAR(20) | 'github' |
| oauth_provider_id | VARCHAR(255) | UNIQUE with provider |
| timezone | VARCHAR(50) | default 'UTC' |
| created_at / updated_at | TIMESTAMPTZ | |

### refresh_tokens
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| token_hash | VARCHAR(128) | SHA-256, UNIQUE |
| expires_at | TIMESTAMPTZ | |
| revoked | BOOLEAN | default false |

### habits
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| title | VARCHAR(150) | |
| description | VARCHAR(500) | nullable |
| category | VARCHAR(20) | enum: 6 categories |
| schedule_type | VARCHAR(20) | 'daily', 'specific_days', 'multiple_daily' |
| schedule_days | SMALLINT[] | ISO weekday 1-7, null=every day |
| times_per_day | SMALLINT | default 1 |
| is_active | BOOLEAN | default true (soft delete) |

### habit_completions
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| habit_id | UUID | FK → habits |
| user_id | UUID | FK → users (denormalized) |
| date | DATE | |
| status | VARCHAR(10) | 'completed' / 'skipped' |
| completion_count | SMALLINT | for multi-daily |
| points_delta | FLOAT | positive or negative |
| UNIQUE(habit_id, date) | | |

### category_scores (materialized, 6 rows per user)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| category | VARCHAR(20) | |
| score | FLOAT | 0-100, clamped |
| streak_days | INTEGER | current |
| longest_streak | INTEGER | all-time |
| UNIQUE(user_id, category) | | |

### quests
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| quest_type | VARCHAR(10) | 'daily' / 'weekly' |
| title | VARCHAR(200) | AI-generated |
| description | VARCHAR(1000) | AI-generated |
| target_category | VARCHAR(20) | |
| criteria_json | JSONB | machine-readable criteria |
| bonus_points | FLOAT | |
| status | VARCHAR(15) | 'active' / 'completed' / 'expired' |
| issued_date | DATE | |
| expires_at | TIMESTAMPTZ | |

### narrations
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| trigger_type | VARCHAR(20) | 'completion' / 'skip' / 'quest_complete' |
| trigger_ref_id | UUID | nullable |
| content | VARCHAR(500) | AI-generated text |

---

## Category System (Soft Neon Palette)

```python
CATEGORIES = {
    "intelligence": {"color": "#A78BFA", "glow": "#C4B5FD", "label": "Intelligence", "icon": "brain"},      # soft neon violet
    "stamina":      {"color": "#34D399", "glow": "#6EE7B7", "label": "Stamina",      "icon": "flame"},      # soft neon emerald
    "sociality":    {"color": "#FBBF24", "glow": "#FDE68A", "label": "Sociality",    "icon": "users"},      # soft neon amber
    "creativity":   {"color": "#FB923C", "glow": "#FDBA74", "label": "Creativity",    "icon": "palette"},   # soft neon orange
    "discipline":   {"color": "#38BDF8", "glow": "#7DD3FC", "label": "Discipline",    "icon": "shield"},    # soft neon sky
    "wellness":     {"color": "#F472B6", "glow": "#F9A8D4", "label": "Wellness",      "icon": "heart"},     # soft neon pink
}
```

Colors are soft neon — vibrant but not harsh, with lighter glow variants for the aura particle effects.

---

## Scoring Algorithm

- **Completion**: `points = 2.0 × (1 + 0.15 × ln(1 + streak_days))` — logarithmic streak bonus (1.7x at 100-day streak)
- **Skip penalty**: `penalty = max(-1.0 × 1.5^(consecutive_skips - 1), -8.0)` — compounding but capped
- **Daily decay**: -0.3 per inactive day per category (lazy evaluation on first access)
- **Score range**: 0–100, clamped
- **Quest bonus**: 3-8 points (daily), 10-20 points (weekly)

---

## API Endpoints (all under `/api/v1`)

### Auth
- `GET /auth/github/login` → redirect URL
- `GET /auth/github/callback` → tokens + user
- `POST /auth/refresh` → new token pair
- `POST /auth/logout` → revoke refresh token

### Users
- `GET /users/me` → profile + all 6 scores
- `PATCH /users/me` → update name/timezone

### Habits
- `POST /habits` → create
- `GET /habits` → list (filter by category, active)
- `GET /habits/{id}` → detail
- `PATCH /habits/{id}` → update
- `DELETE /habits/{id}` → soft-delete

### Completions
- `POST /habits/{id}/complete` → returns completion + updated score + narration
- `POST /habits/{id}/skip` → returns completion + updated score + narration
- `GET /habits/{id}/history` → paginated history

### Dashboard
- `GET /dashboard/today` → today's habits + statuses + scores + active quests
- `GET /dashboard/week?date=2026-03-30` → 7-day grid of habits with completion statuses (read-only for non-today)
- `GET /dashboard/month?date=2026-03-30` → 30-day calendar view with daily completion summaries (read-only)

### Stats
- `GET /stats` → all category scores + streaks
- `GET /stats/history?period=30d` → score snapshots over time

### Quests
- `GET /quests` → active + recent
- `POST /quests/{id}/claim` → claim completed quest reward

---

## Backend Structure

```
backend/
├── alembic/
├── app/
│   ├── main.py              # FastAPI app, middleware, lifespan
│   ├── config.py             # Pydantic Settings
│   ├── database.py           # async engine + session
│   ├── dependencies.py       # get_db, get_current_user
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic request/response
│   ├── api/                  # Route handlers (thin)
│   │   ├── router.py         # aggregates sub-routers
│   │   ├── auth.py, habits.py, dashboard.py, stats.py, quests.py
│   ├── services/             # Business logic
│   │   ├── auth_service.py, habit_service.py, completion_service.py
│   │   ├── stats_engine.py   # scoring algorithm (pure logic)
│   │   ├── quest_service.py, ai_master_service.py
│   ├── core/                 # security.py, oauth.py, constants.py, exceptions.py
│   └── integrations/
│       └── bedrock_client.py # AWS Bedrock wrapper
├── tests/
│   ├── conftest.py           # fixtures: test DB, client, factories
│   ├── unit/                 # stats_engine, completion_service
│   └── integration/          # full API tests
├── pyproject.toml            # uv-managed dependencies
├── uv.lock                   # uv lockfile
├── docker-compose.yml
└── .env.example
```

---

## Frontend Structure

```
frontend/
├── src/
│   ├── main.tsx, App.tsx
│   ├── api/                  # client.ts, *.api.ts per domain
│   ├── hooks/                # TanStack Query hooks per domain
│   ├── stores/               # Zustand: sidebar, master-popup, aura-events, theme
│   ├── types/                # TypeScript interfaces
│   ├── lib/                  # utils.ts, constants.ts, query-client.ts
│   ├── components/
│   │   ├── ui/               # shadcn primitives
│   │   ├── layout/           # AppLayout, Sidebar, Header, UserMenu, ThemeToggle
│   │   ├── habits/           # HabitForm, HabitCard, CategorySelect, ScheduleSelector
│   │   ├── dashboard/        # DashboardTabs, TodayView, WeekView, MonthView, UpcomingHabitCard, StatsPanel, CategoryBar, QuestSection, WeekGrid, MonthCalendar
│   │   ├── aura/             # AuraCanvas, aura-renderer.ts, aura-particles.ts
│   │   └── master/           # MasterPopup, MasterPopupProvider
│   ├── pages/                # LoginPage, DashboardPage, HabitsPage, OAuthCallbackPage
│   └── test/                 # setup.ts, test-utils.tsx, mocks/
├── vite.config.ts
├── vitest.config.ts
└── package.json
```

---

## Frontend Key Decisions

- **State**: TanStack Query for all server state; Zustand for sidebar toggle, master popup visibility, aura flare event queue, theme
- **Auth**: Backend sets httpOnly cookie with JWT; frontend sends `withCredentials: true`
- **Aura visualization**: Canvas 2D API with particle system — **soft-fuzzy, iridescent** aesthetic
  - Soft radial gradient base with Gaussian blur, category-weighted color blending creating an iridescent shimmer
  - Multiple overlapping translucent gradient layers that slowly rotate/shift to produce iridescent color transitions
  - Sine-wave breathing animation (0.8Hz normal, 0.3Hz decayed) modulating radius + opacity
  - 60-120 soft-edged glowing particles (large blur radius) proportional to scores, drifting slowly
  - Flare: burst of 20-40 particles from center on completion, with bloom/glow effect
  - Decay: dim opacity + slow breathing + desaturate on consecutive skips
  - **Alive behavior**: subtle organic randomness in particle drift (Perlin noise or simplex noise for movement), slight pulsation irregularity (breathing isn't perfectly sinusoidal — add jitter), occasional spontaneous micro-flickers in random particles, gentle color temperature shifts over time. The aura should feel like a living organism, never perfectly still or repetitive.
  - Overall feel: ethereal, luminous cloud — not sharp or geometric. Must feel alive and organic.
- **Master popup**: Fixed bottom-center toast with glowing category-colored border, auto-dismiss 6s
- **Design**: Mobile-first responsive design. All layouts, components, and breakpoints designed for mobile first, then enhanced for tablet/desktop.
- **Theme**: Dark and light themes, togglable via header button. Tailwind `class` strategy with `dark` class on `<html>`. Default: dark. Theme preference persisted in localStorage.
- **Forms**: react-hook-form + zod validation

---

## Dashboard Layout

The dashboard has a **Today / Week / Month** tab switcher at the top. Only today's habits have complete/skip buttons — week and month views are read-only overviews.

### Today View (default)
```
Desktop (lg+):                          Mobile:
┌──────────────┬─────────────┐          ┌──────────────┐
│              │   Stats     │          │    Aura      │
│    Aura      │   Panel     │          ├──────────────┤
│  Visualizer  │             │          │  Stats Panel │
│              ├─────────────┤          ├──────────────┤
│              │   Quests    │          │  Upcoming    │
├──────────────┴─────────────┤          ├──────────────┤
│    Today's Habits (cards)  │          │   Quests     │
│   [Complete] [Skip] each   │          └──────────────┘
└────────────────────────────┘
```

### Week View
```
┌──────────────┬─────────────┐
│              │   Stats     │
│    Aura      │   Panel     │
│              ├─────────────┤
│              │   Quests    │
├──────────────┴─────────────┤
│   Mon  Tue  Wed  Thu  Fri  │  ← 7-day grid
│   ✓✓   ✓✗   ✓✓   --  --   │  ← completion status per habit
│   Read-only, no actions    │
└────────────────────────────┘
```

### Month View
```
┌──────────────┬─────────────┐
│              │   Stats     │
│    Aura      │   Panel     │
│              ├─────────────┤
│              │   Quests    │
├──────────────┴─────────────┤
│      March 2026 Calendar   │  ← calendar grid
│   Each day shows completion │  ← color-coded summary
│   rate (e.g. 3/5 habits)   │  ← read-only
└────────────────────────────┘
```

---

## AI Master Prompting

- **System prompt**: "You are Master Aura, a wise and gently humorous mentor in the spirit of Master Oogway. Short, memorable aphorisms. Max 2 sentences. Nature metaphors, playful humor."
- **On completion**: provide habit title, category, streak, score, time of day
- **On skip**: gentle and motivating, never harsh; provide consecutive skip count
- **Quest generation**: structured JSON output with title, description, target_category, bonus_points, criteria object
- **Model**: Haiku for narrations (fast, cheap); Haiku or Opus for quest generation
- **Fallback**: if Bedrock fails, return a predefined wise quote from a local pool

---

## Implementation Phases

### Phase 1: Project Scaffolding
- Backend: `uv init` + `uv add` for FastAPI, SQLAlchemy, asyncpg, alembic, etc. Config, database, docker-compose (Postgres)
- Frontend: Vite + React + TS, Tailwind, ShadcnUI, routing, TanStack Query
- Alembic init + first migration (all tables)

### Phase 2: Auth
- OAuth flow (GitHub)
- JWT issuance/refresh/logout
- Frontend login page, callback handler, RequireAuth guard
- Header with avatar + logout dropdown

### Phase 3: Habits CRUD
- Backend: habit endpoints + service + validation
- Frontend: habits page, form with category select + schedule selector
- Tests for validation, ownership enforcement

### Phase 4: Dashboard + Completions + Stats
- Backend: dashboard endpoint, completion service, stats engine
- Frontend: dashboard layout (Today/Week/Month tabs), upcoming habit cards, complete/skip, stats panel
- Optimistic updates, score recalculation
- Unit tests for stats engine (most critical test file)

### Phase 5: Aura Visualization
- Canvas 2D particle system with breathing animation
- Score-driven color blending, iridescent shimmer
- Flare effect on completion, decay on consecutive skips
- Alive behavior: Perlin noise drift, jitter, micro-flickers
- Aura event store wired to completion flow

### Phase 6: AI Master + Quests
- Bedrock client integration
- Narration generation on complete/skip
- Master popup UI with category-colored glow
- Quest generation, display, and claim flow
- Fallback behavior when AI unavailable

### Phase 7: Polish + Testing
- Integration tests for full flows
- Error handling, loading skeletons, edge cases
- Responsive design verification (mobile-first)
- Rate limiting, CORS, security hardening

---

## Verification Plan

1. **Backend**: `docker-compose up` starts Postgres + API; run `pytest` for unit + integration tests against real DB (testcontainers)
2. **Frontend**: `npm run dev` starts Vite dev server; run `npx vitest` for component + hook tests with MSW mocks
3. **End-to-end manual**:
   - Login via GitHub → see dashboard
   - Add habits across categories → see them on habits page
   - Complete/skip habits → verify score changes, aura flare/dim, master popup appears
   - Switch between Today/Week/Month views → verify read-only behavior for non-today
   - Check quests appear, complete one, verify bonus points
   - Skip habits for several days → verify aura fading
   - Toggle dark/light theme → verify both themes work
