from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Resolve the .env file relative to this file's directory so it is found
# regardless of the current working directory.
_ENV_FILE = Path(__file__).parent / ".env"

try:
    from trading_bot.bot.client import (
        BinanceAPIError,
        BinanceFuturesClient,
        DEFAULT_BASE_URL,
    )
    from trading_bot.bot.logging_config import setup_logging
    from trading_bot.bot.orders import place_order
    from trading_bot.bot.validators import ValidationError, validate_order_args
except ModuleNotFoundError:
    from bot.client import BinanceAPIError, BinanceFuturesClient, DEFAULT_BASE_URL
    from bot.logging_config import setup_logging
    from bot.orders import place_order
    from bot.validators import ValidationError, validate_order_args


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET and LIMIT orders on Binance USDT-M Futures Testnet."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Limit price; required for LIMIT orders")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Binance Futures API base URL (default: {DEFAULT_BASE_URL})",
    )
    return parser


def get_credentials() -> tuple[str, str]:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    missing = [
        name
        for name, value in (
            ("BINANCE_API_KEY", api_key),
            ("BINANCE_API_SECRET", api_secret),
        )
        if not value
    ]
    if missing:
        raise ValidationError(
            "Missing environment variable(s): "
            + ", ".join(missing)
            + ". Create .env from .env.example."
        )

    return api_key or "", api_secret or ""


def print_request_summary(order: dict[str, str]) -> None:
    print("Request summary")
    print(f"  symbol: {order['symbol']}")
    print(f"  side: {order['side']}")
    print(f"  type: {order['type']}")
    print(f"  quantity: {order['quantity']}")
    if order["type"] == "LIMIT":
        print(f"  price: {order['price']}")
        print("  timeInForce: GTC")


def print_order_result(response: dict[str, Any]) -> None:
    print("Order result")
    print(f"  orderId: {response.get('orderId', 'N/A')}")
    print(f"  status: {response.get('status', 'N/A')}")
    print(f"  executedQty: {response.get('executedQty', 'N/A')}")

    avg_price = response.get("avgPrice")
    if avg_price in (None, ""):
        avg_price = response.get("price")
    print(f"  avgPrice: {avg_price if avg_price not in (None, '') else 'N/A'}")


def main() -> int:
    load_dotenv(dotenv_path=_ENV_FILE, override=True)
    logger = setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    try:
        order = validate_order_args(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
        )
        api_key, api_secret = get_credentials()

        print_request_summary(order)

        client = BinanceFuturesClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url=args.base_url,
            logger=logger,
        )
        response = place_order(client, order)
        print_order_result(response)
        return 0
    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2
    except BinanceAPIError as exc:
        logger.error("Order failed: %s", exc)
        print(f"Order failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
