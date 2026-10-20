# Stocks Tracker

API that monitors a list of stocks and shows which ones are
trading below a reference high you define.

## Project conventions

- All code, comments, commit messages and documentation in this
  project must be written in English.

## What it does

You register the stocks you want to follow along with your own
reference high. When you run a check, the API fetches the current
price of each stock from Finnhub, calculates how far it is from
its reference high, and returns the ones that have dropped 5% or more.

Checks run only on demand (for example, when you press a "Check"
button). There is no scheduled or automatic check.

Example response:

| Symbol | Reference high | Current price | Distance from reference |
|--------|----------------|---------------|-------------------------|
| NVDA   | 230.00         | 214.13        | -6.9%                   |

## Rules

- Distance is calculated as:
  (current price - reference high) / reference high × 100.
- If a stock goes above its reference high, that price becomes
  the new reference high.
- The reference high must be split-adjusted.
- The 5% threshold is configurable.

## Tech stack

- Python + FastAPI
- httpx (async calls to Finnhub)
- Pydantic
