import asyncio
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx


class FinnhubError(Exception):
    """Raised when Finnhub cannot provide a valid response."""


@dataclass(frozen=True)
class QuoteResult:
    symbol: str
    current_price: Decimal | None


class FinnhubClient:
    base_url = "https://finnhub.io/api/v1"

    def __init__(self, api_key: str, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-Finnhub-Token": api_key},
            timeout=timeout,
        )
        self._semaphore = asyncio.Semaphore(10)

    async def close(self) -> None:
        await self._client.aclose()

    async def fetch_prices(self, symbols: list[str]) -> list[QuoteResult]:
        return list(await asyncio.gather(*(self._fetch_price(symbol) for symbol in symbols)))

    async def _fetch_price(self, symbol: str) -> QuoteResult:
        async with self._semaphore:
            try:
                response = await self._client.get("/quote", params={"symbol": symbol})
                response.raise_for_status()
                data: Any = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise FinnhubError(f"Finnhub request failed for {symbol}") from exc

        current_price = data.get("c") if isinstance(data, dict) else None
        if current_price is None:
            raise FinnhubError(f"Finnhub returned an invalid quote for {symbol}")

        try:
            price = Decimal(str(current_price))
        except (ArithmeticError, ValueError) as exc:
            raise FinnhubError(f"Finnhub returned an invalid price for {symbol}") from exc

        if not price.is_finite() or price < 0:
            raise FinnhubError(f"Finnhub returned an invalid price for {symbol}")

        return QuoteResult(symbol=symbol, current_price=None if price == 0 else price)


def create_finnhub_client() -> FinnhubClient:
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise FinnhubError("FINNHUB_API_KEY is not configured")
    return FinnhubClient(api_key)
