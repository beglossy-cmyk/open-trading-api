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
            # KIS Open API uses market code and symbol.
            # These field names are placeholders and may need adjustment.
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
        }

        raw = self.client.get(config.PRICE_ENDPOINT, params=params)
        logger.info("Market data response: %s", {k: raw.get(k) for k in raw if k in ["rt_cd", "stck_prpr", "output"]})

        output = raw.get("output")
        if isinstance(output, list) and output:
            item = output[0]
            price_value = item.get("stck_prpr") or item.get("price") or item.get("prpr")
            try:
                return int(price_value)
            except (TypeError, ValueError):
                pass

        if isinstance(raw, dict):
            price_value = raw.get("stck_prpr") or raw.get("price") or raw.get("prpr")
            if price_value is not None:
                try:
                    return int(price_value)
                except (TypeError, ValueError):
                    pass

        logger.error("Unable to parse market price for %s", symbol)
        return None
