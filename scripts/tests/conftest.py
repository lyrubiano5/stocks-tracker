import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.models import Stock


@pytest.fixture
def stocks_by_symbol(session_maker: async_sessionmaker):
    async def query(symbol: str) -> list[Stock]:
        async with session_maker() as session:
            result = await session.execute(
                select(Stock).where(Stock.symbol == symbol)
            )
            return list(result.scalars().all())

    return query
