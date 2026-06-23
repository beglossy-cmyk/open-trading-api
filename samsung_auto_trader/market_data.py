from typing import Any
from samsung_auto_trader import config
from samsung_auto_trader.api_client import ApiClient
from samsung_auto_trader.logger import configure_logger
logger = configure_logger()

class MarketDataService:
    def __init__(self, client: ApiClient):
        self.client = client

    def get_current_price(self, symbol: str) -> int | None:
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
        }
        self.client.headers["tr_id"] = "FHKST01010100"
        raw = self.client.get(config.PRICE_ENDPOINT, params=params)
        output = raw.get("output")
        if isinstance(output, dict):
            price_value = output.get("stck_prpr")
            if price_value:
                try:
                    return int(price_value)
                except (TypeError, ValueError):
                    pass
        logger.error("Unable to parse market price for %s: %s", symbol, raw)
        return None
