import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import Stock
from app.schemas.stocks import (
    BelowThresholdStockResponse,
    CheckResponse,
    CheckedStockResponse,
)
from app.services.finnhub import FinnhubClient, FinnhubError, QuoteResult
from app.services.stock_calculations import (
    calculate_distance_pct,
    should_update_reference_high,
)

router = APIRouter(prefix="/api")


def get_threshold_percent() -> Decimal:
    value = os.getenv("THRESHOLD_PERCENT", "5")
    try:
        threshold = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("THRESHOLD_PERCENT must be a number") from exc
    if not threshold.is_finite() or threshold < 0:
        raise ValueError("THRESHOLD_PERCENT must be a non-negative number")
    return threshold


def get_finnhub_client(request: Request) -> FinnhubClient:
    return request.app.state.finnhub_client


@router.post("/check", response_model=CheckResponse)
async def check_stocks(
    finnhub: FinnhubClient = Depends(get_finnhub_client),
    session: AsyncSession = Depends(get_session),
) -> CheckResponse:
    stocks = list((await session.scalars(select(Stock).order_by(Stock.symbol))).all())
    quotes = await _fetch_quotes(finnhub, [stock.symbol for stock in stocks])
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


async def _fetch_quotes(
    finnhub: FinnhubClient, symbols: list[str]
) -> list[QuoteResult]:
    try:
        return await finnhub.fetch_prices(symbols)
    except FinnhubError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/stocks/below-threshold",
    response_model=list[BelowThresholdStockResponse],
)
async def get_stocks_below_threshold(
    session: AsyncSession = Depends(get_session),
) -> list[BelowThresholdStockResponse]:
    stocks = await session.scalars(
        select(Stock)
        .where(Stock.is_below_threshold.is_(True))
        .order_by(Stock.symbol)
    )
    return [
        BelowThresholdStockResponse(
            symbol=stock.symbol,
            name=stock.name,
            reference_high=stock.reference_high,
            current_price=stock.last_price,
            distance_pct=stock.distance_pct,
        )
        for stock in stocks
    ]
