import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs

from trading_bot.bot.client import BinanceAPIError, BinanceFuturesClient


class BinanceFuturesClientTests(unittest.TestCase):
    @patch("trading_bot.bot.client.time.time", return_value=1234.567)
    @patch("trading_bot.bot.client.requests.request")
    def test_signed_request_adds_timestamp_signature_and_api_key(
        self, mock_request, _mock_time
    ):
        response = Mock()
        response.status_code = 200
        response.text = '{"orderId": 123}'
        response.json.return_value = {"orderId": 123}
        mock_request.return_value = response

        client = BinanceFuturesClient("key", "secret", base_url="https://example.test")
        result = client.signed_request(
            "POST",
            "/fapi/v1/order",
            {"symbol": "BTCUSDT", "quantity": "0.001"},
        )

        self.assertEqual(result, {"orderId": 123})
        kwargs = mock_request.call_args.kwargs
        self.assertEqual(kwargs["method"], "POST")
        self.assertEqual(kwargs["url"], "https://example.test/fapi/v1/order")
        self.assertEqual(kwargs["headers"], {"X-MBX-APIKEY": "key"})
        self.assertEqual(kwargs["params"]["timestamp"], 1234567)
        self.assertIn("signature", kwargs["params"])

        params_without_signature = dict(kwargs["params"])
        params_without_signature.pop("signature")
        self.assertEqual(
            parse_qs("&".join(f"{k}={v}" for k, v in params_without_signature.items())),
            {
                "symbol": ["BTCUSDT"],
                "quantity": ["0.001"],
                "timestamp": ["1234567"],
            },
        )

    @patch("trading_bot.bot.client.requests.request")
    def test_api_error_includes_binance_message(self, mock_request):
        response = Mock()
        response.status_code = 400
        response.text = '{"code": -2019, "msg": "Margin is insufficient."}'
        response.json.return_value = {"code": -2019, "msg": "Margin is insufficient."}
        mock_request.return_value = response

        client = BinanceFuturesClient("key", "secret")

        with self.assertRaisesRegex(BinanceAPIError, "Margin is insufficient"):
            client.signed_request("POST", "/fapi/v1/order", {})


if __name__ == "__main__":
    unittest.main()
