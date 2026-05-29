from typing import Any

from samsung_auto_trader import config
from samsung_auto_trader.api_client import ApiClient
from samsung_auto_trader.logger import configure_logger

logger = configure_logger()


class OrderService:
    def __init__(self, client: ApiClient, account_no: str):
        self.client = client
        self.account_no = account_no

    def submit_order(
        self,
        symbol: str,
        side: str,
        price: int,
        quantity: int,
    ) -> dict[str, Any]:
        order_side = "01" if side == "buy" else "02"
        order_payload = {
            # Placeholder field names for KIS paper order API.
            "CANO": self.account_no,
            "ACNT_PRDT_CD": config.ACCOUNT_PRODUCT_CODE,
            "PDNO": symbol,
            "ORD_DVSN": order_side,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
            "ORD_CMPTP": "00",
            "ORD_PRC_GRTN_CODE": "00",
        }

        logger.info("Submitting %s order for %s at %s KRW qty=%s", side, symbol, price, quantity)
        raw = self.client.post(config.ORDER_ENDPOINT, json_body=order_payload)
        logger.info("Order response: %s", {k: raw.get(k) for k in raw if k in ["rt_cd", "ord_no", "message", "output"]})
        return raw
