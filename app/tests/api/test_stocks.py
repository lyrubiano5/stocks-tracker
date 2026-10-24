from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Stock
from app.services.finnhub import FinnhubError
from app.tests.conftest import FakeFinnhubClient, add_stock


class TestCheckStocksEndpoint:
    @pytest.mark.usefixtures("clean_database")
    async def test_updates_stock_and_skips_zero_price(
        self,
        client,
        session_maker: async_sessionmaker[AsyncSession],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        test_client, set_finnhub_client = client
        await add_stock(
            session_maker, symbol="MSFT", name="Microsoft", reference_high="100"
        )
        await add_stock(
            session_maker, symbol="AAPL", name="Apple", reference_high="200"
        )
        fake = FakeFinnhubClient({"MSFT": Decimal("90"), "AAPL": Decimal("0")})
        set_finnhub_client(fake)
        monkeypatch.setenv("THRESHOLD_PERCENT", "5")

        response = await test_client.post("/api/check")

        assert response.status_code == 200
        assert response.json() == {
            "updated_stocks": [
                {
                    "symbol": "MSFT",
                    "name": "Microsoft",
                    "current_price": "90",
                    "reference_high": "100.000",
                    "distance_pct": "-10.0",
                    "is_below_threshold": True,
                    "reference_high_updated": False,
                }
            ],
            "skipped_symbols": ["AAPL"],
        }
        assert fake.calls == [["AAPL", "MSFT"]]

        async with session_maker() as session:
            stocks = {
                stock.symbol: stock
                for stock in (await session.scalars(select(Stock))).all()
            }
        assert stocks["MSFT"].last_price == Decimal("90.000")
        assert stocks["MSFT"].distance_pct == Decimal("-10.00")
        assert stocks["MSFT"].is_below_threshold is True
        assert stocks["AAPL"].last_price is None

    @pytest.mark.usefixtures("clean_database")
    async def test_updates_reference_high(
        self, client, session_maker: async_sessionmaker[AsyncSession]
    ) -> None:
        test_client, set_finnhub_client = client
        await add_stock(
            session_maker, symbol="NVDA", name="NVIDIA", reference_high="100"
        )
        set_finnhub_client(FakeFinnhubClient({"NVDA": Decimal("110")}))

        response = await test_client.post("/api/check")

        assert response.status_code == 200
        stock = response.json()["updated_stocks"][0]
        assert stock["reference_high"] == "110"
        assert stock["distance_pct"] == "0"
        assert stock["reference_high_updated"] is True

        async with session_maker() as session:
            stored = await session.scalar(select(Stock).where(Stock.symbol == "NVDA"))
        assert stored is not None
        assert stored.reference_high == Decimal("110.000")

    @pytest.mark.usefixtures("clean_database")
    async def test_returns_error_without_persisting_when_finnhub_fails(
        self, client, session_maker: async_sessionmaker[AsyncSession]
    ) -> None:
        test_client, set_finnhub_client = client
        await add_stock(
            session_maker, symbol="TSLA", name="Tesla", reference_high="250"
        )
        set_finnhub_client(
            FakeFinnhubClient({}, error=FinnhubError("Finnhub request failed"))
        )

        response = await test_client.post("/api/check")

        assert response.status_code == 502
        assert response.json() == {"detail": "Finnhub request failed"}

        async with session_maker() as session:
            stored = await session.scalar(select(Stock).where(Stock.symbol == "TSLA"))
        assert stored is not None
        assert stored.reference_high == Decimal("250.000")
        assert stored.last_price is None
        assert stored.distance_pct is None


class TestStocksEndpoint:
    @pytest.mark.usefixtures("clean_database")
    async def test_returns_all_stocks_with_persisted_values(
        self, client, session_maker: async_sessionmaker[AsyncSession]
    ) -> None:
        test_client, set_finnhub_client = client
        await add_stock(
            session_maker,
            symbol="MSFT",
            name="Microsoft",
            reference_high="100",
            last_price="90",
            distance_pct="-10",
        )
        await add_stock(
            session_maker,
            symbol="AAPL",
            name="Apple",
            reference_high="200",
        )
        fake = FakeFinnhubClient({}, error=FinnhubError("Finnhub must not be called"))
        set_finnhub_client(fake)

        response = await test_client.get("/api/stocks")

        assert response.status_code == 200
        assert response.json() == [
            {
                "symbol": "AAPL",
                "name": "Apple",
                "current_price": None,
                "reference_high": "200.000",
                "distance_pct": None,
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft",
                "current_price": "90.000",
                "reference_high": "100.000",
                "distance_pct": "-10.00",
            },
        ]
        assert fake.calls == []


class TestBelowThresholdEndpoint:
    @pytest.mark.usefixtures("clean_database")
    async def test_returns_persisted_values_without_calling_finnhub(
        self, client, session_maker: async_sessionmaker[AsyncSession]
    ) -> None:
        test_client, set_finnhub_client = client
        await add_stock(
            session_maker,
            symbol="AMD",
            name="AMD",
            reference_high="100",
            last_price="92",
            distance_pct="-8",
            is_below_threshold=True,
        )
        await add_stock(
            session_maker,
            symbol="INTC",
            name="Intel",
            reference_high="50",
            last_price="49",
            distance_pct="-2",
            is_below_threshold=False,
        )
        fake = FakeFinnhubClient({}, error=FinnhubError("Finnhub must not be called"))
        set_finnhub_client(fake)

        response = await test_client.get("/api/stocks/below-threshold")

        assert response.status_code == 200
        assert response.json() == [
            {
                "symbol": "AMD",
                "name": "AMD",
                "reference_high": "100.000",
                "current_price": "92.000",
                "distance_pct": "-8.00",
            }
        ]
        assert fake.calls == []
