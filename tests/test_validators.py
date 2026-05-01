import unittest

from trading_bot.bot.validators import ValidationError, validate_order_args


class ValidateOrderArgsTests(unittest.TestCase):
    def test_market_order_is_normalized(self):
        order = validate_order_args("btcusdt", "buy", "market", "0.0010", None)

        self.assertEqual(
            order,
            {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "0.001",
            },
        )

    def test_limit_order_requires_price(self):
        with self.assertRaisesRegex(ValidationError, "--price is required"):
            validate_order_args("BTCUSDT", "BUY", "LIMIT", "0.001", None)

    def test_market_order_rejects_price(self):
        with self.assertRaisesRegex(ValidationError, "--price is only valid"):
            validate_order_args("BTCUSDT", "BUY", "MARKET", "0.001", "70000")

    def test_rejects_nan_quantity(self):
        with self.assertRaisesRegex(ValidationError, "finite number"):
            validate_order_args("BTCUSDT", "BUY", "MARKET", "NaN", None)

    def test_rejects_infinite_price(self):
        with self.assertRaisesRegex(ValidationError, "finite number"):
            validate_order_args("BTCUSDT", "BUY", "LIMIT", "0.001", "Infinity")


if __name__ == "__main__":
    unittest.main()
