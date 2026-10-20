# TODO

- [ ] 0. Set up Docker: `Dockerfile` and `docker-compose.yml` with two
      services: the FastAPI app with auto-reload reading `.env`, and
      PostgreSQL with a volume to persist data.
- [ ] 1. Create the frontend as a simple HTML page served by FastAPI,
      with a "Check" button (not functional yet) and a hardcoded
      result: "NVDA is 10% below its reference high".
- [ ] 2. Create the database with async SQLAlchemy and PostgreSQL,
      with a stocks table that stores the symbol and the reference high.
- [ ] 3. Create a script to load some stocks with their reference
      high into the table.
- [ ] 4. Create the endpoint that reads the stocks from the table,
      fetches their current price from Finnhub, calculates the
      distance, and returns only the ones that dropped 5% or more.
- [ ] 5. Connect the frontend to the backend.
- [ ] 6. Update the reference high when a stock goes above it.
