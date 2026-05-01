from __future__ import annotations

from decimal import Decimal, InvalidOperation


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(ValueError):
    """Raised when CLI input is invalid."""


def normalize_symbol(symbol: str | None) -> str:
    if not symbol:
        raise ValidationError("--symbol is required.")

    normalized = symbol.strip().upper()
    if not normalized:
        raise ValidationError("--symbol cannot be empty.")
    if not normalized.isalnum():
        raise ValidationError("--symbol must contain only letters and numbers.")
    if not normalized.endswith("USDT"):
        raise ValidationError("Only USDT-M futures symbols are supported, e.g. BTCUSDT.")
    return normalized


def normalize_side(side: str | None) -> str:
    if not side:
        raise ValidationError("--side is required.")

    normalized = side.strip().upper()
    if normalized not in VALID_SIDES:
        raise ValidationError("--side must be BUY or SELL.")
    return normalized


def normalize_order_type(order_type: str | None) -> str:
    if not order_type:
        raise ValidationError("--type is required.")

    normalized = order_type.strip().upper()
    if normalized not in VALID_ORDER_TYPES:
        raise ValidationError("--type must be MARKET or LIMIT.")
    return normalized


def parse_positive_decimal(value: str | None, field_name: str) -> str:
    if value is None:
        raise ValidationError(f"--{field_name} is required.")

    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"--{field_name} must be a valid number.") from None

    if not parsed.is_finite():
        raise ValidationError(f"--{field_name} must be a finite number.")

    if parsed <= 0:
        raise ValidationError(f"--{field_name} must be greater than zero.")

    return format(parsed.normalize(), "f")


def validate_order_args(
    symbol: str | None,
    side: str | None,
    order_type: str | None,
    quantity: str | None,
    price: str | None,
) -> dict[str, str]:
    normalized_type = normalize_order_type(order_type)

    order = {
        "symbol": normalize_symbol(symbol),
        "side": normalize_side(side),
        "type": normalized_type,
        "quantity": parse_positive_decimal(quantity, "quantity"),
    }

    if normalized_type == "LIMIT":
        order["price"] = parse_positive_decimal(price, "price")
    elif price is not None:
        raise ValidationError("--price is only valid for LIMIT orders.")

    return order
