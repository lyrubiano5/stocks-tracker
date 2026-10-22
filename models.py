from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    reference_high: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    last_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    distance_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_below_threshold: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)