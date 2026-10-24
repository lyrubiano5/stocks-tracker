import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Stock
from app.schemas.stocks import CheckResponse, CheckedStockResponse
from app.services.finnhub import FinnhubClient
from app.services.stock_calculations import (
    calculate_distance_pct,
    should_update_reference_high,
)


def get_threshold_percent() -> Decimal:
    value = os.getenv("THRESHOLD_PERCENT", "5")
    try:
        threshold = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("THRESHOLD_PERCENT must be a number") from exc
    if not threshold.is_finite() or threshold < 0:
        raise ValueError("THRESHOLD_PERCENT must be a non-negative number")
    return threshold


async def check_stocks(
    session: AsyncSession, finnhub: FinnhubClient
) -> CheckResponse:
    stocks = list((await session.scalars(select(Stock).order_by(Stock.symbol))).all())
    quotes = await finnhub.fetch_prices([stock.symbol for stock in stocks])

    threshold = get_threshold_percent()
    checked_at = datetime.now(timezone.utc)
    updated_stocks: list[CheckedStockResponse] = []
    skipped_symbols: list[str] = []

    for stock, quote in zip(stocks, quotes):
        if quote.current_price is None:
            skipped_symbols.append(stock.symbol)
            continue

        reference_high_updated = should_update_reference_high(
            quote.current_price, stock.reference_high
        )
        reference_high = (
            quote.current_price if reference_high_updated else stock.reference_high
        )
        distance_pct = calculate_distance_pct(quote.current_price, reference_high)
        is_below_threshold = distance_pct <= -threshold

        stock.reference_high = reference_high
        stock.last_price = quote.current_price
        stock.distance_pct = distance_pct
        stock.is_below_threshold = is_below_threshold
        stock.last_checked_at = checked_at
        updated_stocks.append(
            CheckedStockResponse(
                symbol=stock.symbol,
                name=stock.name,
                current_price=quote.current_price,
                reference_high=reference_high,
                distance_pct=distance_pct,
                is_below_threshold=is_below_threshold,
                reference_high_updated=reference_high_updated,
            )
        )

    await session.commit()
    return CheckResponse(
        updated_stocks=updated_stocks,
        skipped_symbols=skipped_symbols,
    )
