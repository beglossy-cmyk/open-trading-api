import os
from datetime import time
from pathlib import Path

# Environment variables for credentials and accounts
GH_ACCOUNT = os.getenv("GH_ACCOUNT")
GH_APPKEY = os.getenv("GH_APPKEY")
GH_APPSECRET = os.getenv("GH_APPSECRET")

BASE_API_URL = "https://openapivts.koreainvestment.com:29443"
TOKEN_ENDPOINT = "/oauth2/tokenP"
PRICE_ENDPOINT = "/uapi/domestic-stock/v1/quotations/inquire-price"
BALANCE_ENDPOINT = "/uapi/domestic-stock/v1/trading/inquire-balance"
ORDER_ENDPOINT = "/uapi/domestic-stock/v1/trading/order"

TRADING_SYMBOL = "005930"
ORDER_PRICE_OFFSET = 1000  # KRW offset for buy/sell limit orders
TRADING_START = time(hour=9, minute=10)
TRADING_END = time(hour=15, minute=30)
POLL_INTERVAL_SECONDS = 60
ORDER_CONFIRM_INTERVAL_SECONDS = 10
API_TIMEOUT_SECONDS = 10
MAX_API_RETRIES = 2
TOKEN_CACHE_PATH = Path(__file__).parent / "token_cache.json"

# Generic account product code for domestic stock account
ACCOUNT_PRODUCT_CODE = "01"
