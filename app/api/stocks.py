from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import Stock
from app.schemas.stocks import (
    BelowThresholdStockResponse,
    CheckResponse,
    StockResponse,
)
from app.services.finnhub import FinnhubClient, FinnhubError
from app.services.stock_checker import check_stocks as run_stock_check

router = APIRouter(prefix="/api")


def get_finnhub_client(request: Request) -> FinnhubClient:
    return request.app.state.finnhub_client


@router.post("/check", response_model=CheckResponse)
async def check_stocks(
    finnhub: FinnhubClient = Depends(get_finnhub_client),
    session: AsyncSession = Depends(get_session),
) -> CheckResponse:
    try:
        return await run_stock_check(session, finnhub)
    except FinnhubError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/stocks", response_model=list[StockResponse])
async def get_stocks(
    session: AsyncSession = Depends(get_session),
) -> list[StockResponse]:
    stocks = await session.scalars(select(Stock).order_by(Stock.symbol))
    return [
        StockResponse(
            symbol=stock.symbol,
            name=stock.name,
            current_price=stock.last_price,
            reference_high=stock.reference_high,
            distance_pct=stock.distance_pct,
        )
        for stock in stocks
    ]


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
