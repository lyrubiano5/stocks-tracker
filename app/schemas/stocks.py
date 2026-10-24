from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CheckedStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    name: str
    current_price: Decimal
    reference_high: Decimal
    distance_pct: Decimal
    is_below_threshold: bool
    reference_high_updated: bool


class CheckResponse(BaseModel):
    updated_stocks: list[CheckedStockResponse]
    skipped_symbols: list[str]


class BelowThresholdStockResponse(BaseModel):
    symbol: str
    name: str
    reference_high: Decimal
    current_price: Decimal | None
    distance_pct: Decimal | None
