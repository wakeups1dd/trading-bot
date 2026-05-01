# Binance Futures Testnet Trading Bot

A small Python 3 CLI for placing simplified MARKET and LIMIT orders on Binance USDT-M Futures Testnet using the REST API directly with `requests`.

## Features

- Uses `https://testnet.binancefuture.com` by default.
- Loads `BINANCE_API_KEY` and `BINANCE_API_SECRET` from `.env`.
- Signs REST requests with HMAC SHA256.
- Places MARKET and LIMIT orders for BUY and SELL sides.
- Validates CLI input before sending requests.
- Logs API requests, responses, and errors to `logs/trading_bot.log`.
- Prints a concise request summary and order result.

## Setup

```powershell
cd trading_bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add your Binance Futures Testnet API key and secret:

```text
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

## Testnet Instructions

1. Open the Binance Futures Testnet site.
2. Sign in or create a testnet account.
3. Create API credentials for USDT-M Futures Testnet.
4. Add the API key and secret to `.env`.
5. Make sure your testnet account has test USDT before placing orders.

This project is intended for testnet only. The default API host is:

```text
https://testnet.binancefuture.com
```

## Usage

Run commands from the `trading_bot` directory.

Place a MARKET buy:

```powershell
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Place a LIMIT sell:

```powershell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

Optional custom base URL:

```powershell
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --base-url https://testnet.binancefuture.com
```

## CLI Arguments

- `--symbol`: Required. USDT-M symbol such as `BTCUSDT`.
- `--side`: Required. `BUY` or `SELL`.
- `--type`: Required. `MARKET` or `LIMIT`.
- `--quantity`: Required. Positive order quantity.
- `--price`: Required for `LIMIT`; invalid for `MARKET`.
- `--base-url`: Optional. Defaults to Binance Futures Testnet.

## Output

The CLI prints:

- Request summary.
- `orderId`.
- `status`.
- `executedQty`.
- `avgPrice` when available.

Errors are printed clearly to stderr and written to `logs/trading_bot.log`.

## Assumptions

- This bot only targets Binance USDT-M Futures Testnet.
- LIMIT orders use `timeInForce=GTC`.
- Symbol precision, quantity precision, minimum notional, leverage, margin mode, and position mode are enforced by Binance. This CLI performs basic local validation before sending the order.
- API credentials are read from `.env` in the current working directory.

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  cli.py
  README.md
  requirements.txt
  .env.example
  logs/.gitkeep
```
