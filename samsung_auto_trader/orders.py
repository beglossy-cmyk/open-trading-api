from typing import Any
from samsung_auto_trader import config
from samsung_auto_trader.api_client import ApiClient
from samsung_auto_trader.logger import configure_logger
logger = configure_logger()

class OrderService:
    def __init__(self, client: ApiClient, account_no: str):
        self.client = client
        self.account_no = account_no

    def submit_order(self, symbol: str, side: str, price: int, quantity: int) -> dict[str, Any]:
        tr_id = "VTTC0802U" if side == "buy" else "VTTC0801U"
        self.client.headers["tr_id"] = tr_id

        price = round(price / 500) * 500  # 500원 단위 맞추기
        order_payload = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": config.ACCOUNT_PRODUCT_CODE,
            "PDNO": symbol,
            "ORD_DVSN": "00",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
        }
        logger.info("Submitting %s order for %s at %s KRW qty=%s", side, symbol, price, quantity)
        raw = self.client.post("/uapi/domestic-stock/v1/trading/order-cash", json_body=order_payload)
        logger.info("Order response: %s", {k: raw.get(k) for k in raw if k in ["rt_cd", "msg1", "output"]})
        return raw
