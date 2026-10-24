import asyncio
from decimal import Decimal
from sqlalchemy import select
from app.db.database import async_session_maker
from app.db.models import Stock

STOCKS_DATA = [
    ("Microsoft", "546.000", "MSFT"),
    ("Cloudflare", "310.000", "NET"),
    ("Novo Nordisk", "39.560", "NVO"),
    ("Ulta Beauty", "624.000", "ULTA"),
    ("Booking", "162.000", "BKNG"),
    ("RTX", "192.000", "RTX"),
    ("PDD", "79.000", "PDD"),
    ("Micron", "872.000", "MU"),
    ("GE Vernova", "826.000", "GEV"),
]


async def seed_stocks(session_maker=async_session_maker) -> None:
    async with session_maker() as session:
        symbols = [s.upper().replace(" ", "") for _, _, s in STOCKS_DATA]
        result = await session.execute(select(Stock).where(Stock.symbol.in_(symbols)))
        existing = {s.symbol: s for s in result.scalars().all()}

        for name, ref_high, symbol in STOCKS_DATA:
            norm_symbol = symbol.upper().replace(" ", "")
            ref_high_decimal = Decimal(ref_high)

            if norm_symbol in existing:
                existing[norm_symbol].reference_high = ref_high_decimal
            else:
                session.add(Stock(
                    name=name,
                    symbol=norm_symbol,
                    reference_high=ref_high_decimal
                ))

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_stocks())
