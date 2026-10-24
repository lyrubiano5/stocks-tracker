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
- [ ] 5. Update the frontend to show a table with all the stocks:
      symbol, current price, reference high and distance. Use
      hardcoded data for now. Add a button that filters the table
      to show only the stocks that dropped 5% or more.
- [ ] 6. Create an endpoint that returns all the stocks with their
      current price, reference high and distance, with an optional
      filter for the ones that dropped 5% or more.
- [ ] 7. Connect the frontend to the backend: the "Check" button
      updates the prices, the table loads from the endpoint, and
      the filter button uses the endpoint's filter.
