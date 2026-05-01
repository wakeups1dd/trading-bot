from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests


DEFAULT_BASE_URL = "https://testnet.binancefuture.com"


class BinanceAPIError(Exception):
    """Raised when Binance returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 10,
        logger: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logger

    def signed_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        request_params = dict(params or {})
        request_params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(request_params, doseq=True)
        signature = hmac.new(
            self.api_secret,
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        request_params["signature"] = signature

        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key}

        self._log_info(
            "API request method=%s url=%s params=%s",
            method.upper(),
            url,
            self._redact_signature(request_params),
        )

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                params=request_params,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self._log_exception("Network failure: %s", exc)
            raise BinanceAPIError(f"Network failure: {exc}") from exc

        response_text = response.text
        self._log_info(
            "API response status_code=%s body=%s",
            response.status_code,
            response_text,
        )

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response_text}

        if response.status_code >= 400:
            message = payload.get("msg") if isinstance(payload, dict) else response_text
            code = payload.get("code") if isinstance(payload, dict) else None
            detail = f"Binance API error {response.status_code}"
            if code is not None:
                detail += f" code={code}"
            if message:
                detail += f": {message}"
            raise BinanceAPIError(detail, response.status_code)

        if not isinstance(payload, dict):
            raise BinanceAPIError("Unexpected Binance API response format.")

        return payload

    @staticmethod
    def _redact_signature(params: dict[str, Any]) -> dict[str, Any]:
        redacted = dict(params)
        if "signature" in redacted:
            redacted["signature"] = "***"
        return redacted

    def _log_info(self, message: str, *args: Any) -> None:
        if self.logger:
            self.logger.info(message, *args)

    def _log_exception(self, message: str, *args: Any) -> None:
        if self.logger:
            self.logger.exception(message, *args)

