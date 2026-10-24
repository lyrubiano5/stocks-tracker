# AGENTS.md

## Project Overview

Stocks Tracker is a FastAPI application that monitors US-listed stocks and
alerts when they drop by at least a configurable percentage below a reference
high. It includes a web interface, a JSON API, and PostgreSQL persistence.

## Tech Stack

- Python 3.12
- FastAPI and Uvicorn
- httpx for asynchronous Finnhub calls
- Pydantic
- SQLAlchemy 2 with asyncpg
- PostgreSQL 16
- Alembic
- Docker and Docker Compose
- pytest and pytest-asyncio

## Architecture

- **Backend**: FastAPI app with health, stock listing, filtering, and on-demand
  check endpoints.
- **Database**: PostgreSQL with a `stocks` table containing stock identity,
  reference high, latest price, distance, threshold status, and check time.
- **Frontend**: Static HTML page served at `/home`, with controls to update
  prices and filter stocks below the threshold.
- **External API**: Finnhub quote endpoint for current prices of US-listed
  stocks.
- **Migrations and seed**: Alembic manages the schema; `scripts/seed_stocks.py`
  loads the initial stock list.

## Key Rules

- Distance = `(current price - reference high) / reference high * 100`.
- The reference high updates when the current price exceeds it.
- Reference highs must be split-adjusted.
- The 5% threshold is configurable with `THRESHOLD_PERCENT`.
- Checks run on demand only; there is no scheduling.
- A Finnhub price of `0` causes the stock to be skipped without updating it.
- If Finnhub fails, the API returns an error and no check changes are saved.
- Prices are in US dollars because only US stock exchanges are queried.

## Conventions

- All code, comments, commit messages, and documentation must be written in
  English.
- Store secrets in `.env`; `.env` is gitignored.
- Use a Python virtual environment only for local tooling if needed; normal
  development and all project commands run inside Docker.
- Follow PEP 8.
- Order imports in three groups separated by a blank line:
  1. Standard library (for example, `os`, `asyncio`)
  2. Third-party packages (for example, `fastapi`, `sqlalchemy`)
  3. Local modules (for example, `models`, `database`)
- Sort imports alphabetically within each group.
- Do not leave unused imports.
- Use type hints in all function signatures.

## Environment Rules

- Never install packages or run Python, pip, or project tooling directly on
  the host machine.
- Run commands inside Docker, for example:
  `docker compose run --rm app <command>` or
  `docker compose exec app <command>`.
- Never guess package versions. Install packages inside the container and pin
  the versions actually installed in `requirements.txt`.


## Project Structure

- `app/api/`: endpoints.
- `app/schemas/`: Pydantic schemas.
- `app/services/`: business logic and the Finnhub client.
- `app/db/`: database setup and models.
- `app/tests/`: backend tests, mirroring the structure of `app/`.
- `frontend/`: static HTML page.
- `scripts/`: standalone tools, such as the seed script, with their
  tests in `scripts/tests/`.
- `conftest.py` (root): test database fixtures shared by all tests.

## Testing Conventions

- Group tests in classes by feature or endpoint, without inheritance.
- Shared fixtures, fakes and helpers go in conftest.py, not in test files.
- Use the stocks_test database, never mocks of the database session.
- Never call external APIs in tests. Replace dependencies with
  app.dependency_overrides.

## Git Rules

- Never run git commit, git push or any command that changes git
  history. The user reviews and commits all changes.
