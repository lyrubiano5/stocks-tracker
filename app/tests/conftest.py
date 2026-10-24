from collections.abc import AsyncIterator, Callable
from decimal import Decimal

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.stocks import get_finnhub_client
from app.db.database import get_session
from app.db.models import Stock
from app.main import app
from app.services.finnhub import QuoteResult


class FakeFinnhubClient:
    def __init__(
        self, quotes: dict[str, Decimal], error: Exception | None = None
    ) -> None:
        self.quotes = quotes
        self.error = error
        self.calls: list[list[str]] = []

    async def fetch_prices(self, symbols: list[str]) -> list[QuoteResult]:
        self.calls.append(symbols)
        if self.error is not None:
            raise self.error
        return [
            QuoteResult(
                symbol=symbol,
                current_price=(
                    None
                    if (price := self.quotes.get(symbol)) == Decimal("0")
                    else price
                ),
            )
            for symbol in symbols
        ]


@pytest_asyncio.fixture
async def client(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[tuple[httpx.AsyncClient, Callable[[FakeFinnhubClient], None]]]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    def set_finnhub_client(fake: FakeFinnhubClient) -> None:
        app.dependency_overrides[get_finnhub_client] = lambda: fake

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as test_client:
        yield test_client, set_finnhub_client

    app.dependency_overrides.clear()


async def add_stock(
    session_maker: async_sessionmaker[AsyncSession],
    *,
    symbol: str,
    name: str,
    reference_high: str,
    last_price: str | None = None,
    distance_pct: str | None = None,
    is_below_threshold: bool = False,
) -> None:
    async with session_maker() as session:
        session.add(
            Stock(
                symbol=symbol,
                name=name,
                reference_high=Decimal(reference_high),
                last_price=Decimal(last_price) if last_price is not None else None,
                distance_pct=(
                    Decimal(distance_pct) if distance_pct is not None else None
                ),
                is_below_threshold=is_below_threshold,
            )
        )
        await session.commit()
