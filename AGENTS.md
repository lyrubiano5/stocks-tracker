# AGENTS.md

## Project Overview
Stocks Tracker API - monitors stocks and alerts when they drop 5%+ below a reference high.

## Tech Stack
- Python + FastAPI
- httpx (async Finnhub calls)
- Pydantic
- async SQLAlchemy + PostgreSQL (planned)
- Docker + docker-compose (planned)



## Architecture (Planned)
- **Backend**: FastAPI app with endpoints for stock checks
- **Database**: PostgreSQL with `stocks` table (symbol, reference_high)
- **Frontend**: Simple HTML page served by FastAPI with "Check" button
- **External API**: Finnhub for current prices

## Key Rules (from README)
- Distance = (current - reference_high) / reference_high × 100
- Reference high updates when price exceeds it
- Reference high must be split-adjusted
- 5% threshold is configurable
- Checks run on-demand only (no scheduling)

## Conventions
- All code, comments, commits, docs in English
- `.env` for secrets (gitignored)
- Python virtual env in `.venv/` or `venv/` (gitignored)

## Current State
Project is at TODO stage - no implementation yet. See TODO.md for planned tasks.

## Environment rules

- Never install packages or run Python, pip, or any project tooling
  directly on the host machine.
- Everything runs inside Docker. Use `docker compose run --rm app <command>`
  or `docker compose exec app <command>` (e.g. pip, python, pytest, alembic).
- Never guess package versions. Install inside the container and pin
  the versions actually installed in requirements.txt.
