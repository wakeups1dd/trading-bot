from __future__ import annotations

from typing import Any

from .client import BinanceFuturesClient


def place_order(client: BinanceFuturesClient, order: dict[str, str]) -> dict[str, Any]:
    params: dict[str, Any] = {
        "symbol": order["symbol"],
        "side": order["side"],
        "type": order["type"],
        "quantity": order["quantity"],
    }

    if order["type"] == "LIMIT":
        params.update(
            {
                "price": order["price"],
                "timeInForce": "GTC",
            }
        )

    return client.signed_request("POST", "/fapi/v1/order", params)

