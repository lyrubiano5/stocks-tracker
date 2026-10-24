from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.models import Stock
from scripts.seed_stocks import STOCKS_DATA, seed_stocks


class TestSeedStocks:
    async def test_creates_stock_when_it_does_not_exist(
        self,
        session_maker: async_sessionmaker,
        clean_database: None,
        stocks_by_symbol: Callable[[str], Awaitable[list[Stock]]],
    ) -> None:
        # Preparation
        symbol = "MSFT"

        # Execution
        await seed_stocks(session_maker)

        # Checks
        stocks = await stocks_by_symbol(symbol)
        assert len(stocks) == 1
        assert stocks[0].name == "Microsoft"
        assert stocks[0].reference_high == 546

    async def test_updates_stock_when_it_already_exists(
        self,
        session_maker: async_sessionmaker,
        clean_database: None,
        stocks_by_symbol: Callable[[str], Awaitable[list[Stock]]],
    ) -> None:
        # Preparation
        name, _, symbol = STOCKS_DATA[0]
        async with session_maker() as session:
            session.add(Stock(name=name, symbol=symbol, reference_high=100))
            await session.commit()

        # Execution
        await seed_stocks(session_maker)

        # Checks
        stocks = await stocks_by_symbol(symbol)
        assert len(stocks) == 1
        assert stocks[0].reference_high == 546
