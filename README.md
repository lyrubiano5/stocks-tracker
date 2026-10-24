# Stocks Tracker

Stocks Tracker is a small FastAPI application that monitors a personal list
of US-listed stocks. It compares the latest prices from Finnhub with a
reference high for each stock and highlights stocks trading at or below the
configured drop threshold.

The project includes a lightweight web interface, a JSON API, and PostgreSQL
persistence. Price checks are run on demand; the application does not use a
scheduler.

## What the app does

- Stores each stock's name, symbol, reference high, latest price, and distance
  from the reference high.
- Fetches current prices asynchronously from Finnhub when a check is run.
- Updates a stock's reference high when its current price exceeds the stored
  value.
- Identifies stocks whose distance is at or below the configured threshold
  (5% by default).
- Skips a stock when Finnhub returns a price of `0`.
- Returns an error and persists no changes if Finnhub fails during a check.

### Web interface

Open `http://localhost:8000/home` after starting the application. The page:

- Displays all seeded stocks and their current persisted values.
- Updates prices with the **Update prices** button.
- Filters the table to show stocks down by at least the configured threshold.
- Shows prices in US dollars.

### API endpoints

- `GET /health` - application health check.
- `GET /api/stocks` - returns all stocks and their persisted values.
- `GET /api/stocks/below-threshold` - returns only stocks below the threshold.
- `POST /api/check` - fetches current prices and updates the database.

## Rules

- Distance is calculated as:

  `(current price - reference high) / reference high * 100`.

- If a current price exceeds the reference high, it becomes the new reference
  high.
- Reference highs must be split-adjusted.
- The threshold is configurable with `THRESHOLD_PERCENT` and defaults to 5%.
- Checks run only on demand.
- If Finnhub returns a price of `0`, that stock is skipped and its stored data
  is not updated.
- If Finnhub fails or returns an invalid response, the API returns an error
  and no stock changes are saved for that check.
- Prices are expressed in US dollars because the application only queries
  stocks listed on US stock exchanges.

## Tech stack

- Python 3.12
- FastAPI for the web API
- Uvicorn as the ASGI server
- httpx for asynchronous Finnhub requests
- Pydantic for API schemas
- SQLAlchemy 2 with the async PostgreSQL driver `asyncpg`
- PostgreSQL 16 for persistence
- Alembic for database migrations
- Docker and Docker Compose for the application and database services
- pytest and pytest-asyncio for automated tests

## Run with Docker

### Prerequisites

- Docker with Docker Compose
- A Finnhub API key

### First-time setup

1. Create the environment file:

   ```bash
   cp .env.example .env
   ```

2. Set `FINNHUB_API_KEY` in `.env`. The other example values work with the
   provided Docker Compose configuration.

3. Build and start the services:

   ```bash
   docker compose up --build -d
   ```

4. Apply the database migrations:

   ```bash
   docker compose run --rm app alembic upgrade head
   ```

5. Load the initial stock list:

   ```bash
   docker compose run --rm app python scripts/seed_stocks.py
   ```

The API is available at `http://localhost:8000`, and the web interface is at
`http://localhost:8000/home`.

To stop the services while keeping the PostgreSQL volume:

```bash
docker compose down
```

## Run tests

Start the services if they are not already running:

```bash
docker compose up -d
```

Then run the test suite inside the application container:

```bash
docker compose run --rm app pytest
```

The tests create the `stocks_test` PostgreSQL database automatically. No
manual test-database setup is required; the containers only need to be
running.

## Configuration

Environment variables are read from `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `FINNHUB_API_KEY` | Finnhub API key | Required |
| `DATABASE_URL` | Async PostgreSQL connection URL | Provided in `.env.example` |
| `THRESHOLD_PERCENT` | Drop threshold percentage | `5` |
| `PORT` | Application port configuration | `8000` |

The supplied Docker Compose setup exposes the application on port `8000` and
PostgreSQL on port `5432`.
