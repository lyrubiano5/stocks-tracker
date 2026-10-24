---
name: finnhub-api
description: How to fetch stock prices from the Finnhub API in this project. Use this skill whenever a task involves calling Finnhub, getting current stock prices, or handling Finnhub responses.
---

# Finnhub API

## Authentication
- Base URL: https://finnhub.io/api/v1
- Send the API key in the `X-Finnhub-Token` header. Never put it in the URL.
- Read the key from the `FINNHUB_API_KEY` environment variable. Never hardcode it.

## Quote endpoint
- `GET /quote?symbol=<SYMBOL>` returns the current price of a stock.
- Response fields:
  - `c`: current price
  - `d`: change from previous close
  - `dp`: percent change from previous close
  - `h`: high of the day
  - `l`: low of the day
  - `o`: open price of the day
  - `pc`: previous close price
  - `t`: timestamp (Unix seconds)
- For this project, use `c` as the current price.

## How to call it
- Use `httpx.AsyncClient` (async). Never use `requests`, because it blocks the event loop.
- Reuse a single client instead of creating one per request.
- Always set a timeout (e.g. 10 seconds).
- When fetching several stocks, request them concurrently with `asyncio.gather`.

## Limits and errors
- The free plan allows 60 requests per minute. Limit concurrency (e.g. with `asyncio.Semaphore`) so we never exceed it.
- HTTP 429 means the rate limit was exceeded.
- HTTP 401 or 403 means the API key is missing or invalid.
- Finnhub does NOT return an error for unknown symbols. It returns HTTP 200
  with `c`, `h`, `l`, `o`, `pc` and `t` set to 0, and `d` and `dp` set to null.
  If `c` is 0, treat the symbol as invalid or without data, and skip it.
- When modeling the response with Pydantic, `d` and `dp` must be nullable.

