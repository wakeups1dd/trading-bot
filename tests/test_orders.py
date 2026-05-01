import unittest

from trading_bot.bot.orders import place_order


class FakeClient:
    def __init__(self):
        self.calls = []

    def signed_request(self, method, endpoint, params):
        self.calls.append((method, endpoint, params))
        return {"orderId": 123, "status": "NEW"}


class PlaceOrderTests(unittest.TestCase):
    def test_market_order_uses_required_params_only(self):
        client = FakeClient()

        response = place_order(
            client,
            {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "0.001",
            },
        )

        self.assertEqual(response["orderId"], 123)
        self.assertEqual(
            client.calls,
            [
                (
                    "POST",
                    "/fapi/v1/order",
                    {
                        "symbol": "BTCUSDT",
                        "side": "BUY",
                        "type": "MARKET",
                        "quantity": "0.001",
                    },
                )
            ],
        )

    def test_limit_order_adds_price_and_gtc(self):
        client = FakeClient()

        place_order(
            client,
            {
                "symbol": "BTCUSDT",
                "side": "SELL",
                "type": "LIMIT",
                "quantity": "0.001",
                "price": "70000",
            },
        )

        self.assertEqual(client.calls[0][2]["price"], "70000")
        self.assertEqual(client.calls[0][2]["timeInForce"], "GTC")


if __name__ == "__main__":
    unittest.main()
