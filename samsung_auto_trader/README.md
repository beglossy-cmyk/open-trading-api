# Samsung Electronics Auto Trader

A simple Python mock trading project for Samsung Electronics (`005930`) using Korea Investment & Securities Open API.

## Structure

- `main.py` - entrypoint for the trading loop.
- `config.py` - environment variables, endpoints, and trading window settings.
- `auth.py` - token caching and auth endpoint logic.
- `api_client.py` - REST client with retry and timeout handling.
- `market_data.py` - current price retrieval.
- `account.py` - balance and holdings retrieval.
- `orders.py` - order submission logic.
- `trader.py` - trading loop and execution confirmation.
- `logger.py` - logging configuration.
- `token_cache.json` - cached token for same-day reuse.

## Requirements

- Python 3.10+
- `requests`

Install dependencies:

```bash
cd samsung_auto_trader
python -m pip install -r requirements.txt
```

## Environment Variables

Set the following environment variables before running:

- `GH_ACCOUNT` - account number for mock trading
- `GH_APPKEY` - Korea Investment Open API app key
- `GH_APPSECRET` - Korea Investment Open API app secret

Example (Linux/macOS):

```bash
export GH_ACCOUNT="your_account_number"
export GH_APPKEY="your_appkey"
export GH_APPSECRET="your_appsecret"
```

## Run the Trader

Run from the repository root:

```bash
python -m samsung_auto_trader.main
```

The trader will:

1. Authenticate once and reuse the token for the same day.
2. Poll the current price for `005930`.
3. Submit a buy order at current price minus `1000` KRW.
4. Submit a sell order at current price plus `1000` KRW.
5. Confirm execution by checking holdings and balance after each order.
6. Run only between `09:10` and `15:30`.

## Notes

- The project is polling-based only.
- The token cache is stored in `token_cache.json`.
- API field names are intentionally isolated and may need adjustment to match the exact KIS Open API schema.
- This implementation is for mock trading only and is conservative about repeated API calls.
