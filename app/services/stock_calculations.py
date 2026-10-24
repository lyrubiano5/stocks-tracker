from decimal import Decimal


def should_update_reference_high(
    current_price: Decimal, reference_high: Decimal
) -> bool:
    return current_price > reference_high


def calculate_distance_pct(
    current_price: Decimal, reference_high: Decimal
) -> Decimal:
    if reference_high <= 0:
        raise ValueError("reference_high must be greater than zero")
    return (current_price - reference_high) / reference_high * Decimal("100")
