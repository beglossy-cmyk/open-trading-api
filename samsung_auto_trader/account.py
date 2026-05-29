from dataclasses import dataclass
from typing import Any

from samsung_auto_trader import config
from samsung_auto_trader.api_client import ApiClient
from samsung_auto_trader.logger import configure_logger

logger = configure_logger()


@dataclass
class AccountSummary:
    available_cash: int
    total_asset: int
    holdings: list[dict[str, Any]]
    raw: dict[str, Any]


class AccountService:
    def __init__(self, client: ApiClient, account_no: str):
        self.client = client
        self.account_no = account_no

    def get_balance_and_holdings(self) -> AccountSummary:
        params = {
            # Placeholder fields for KIS balance endpoint.
            "CANO": self.account_no,
            "ACNT_PRDT_CD": config.ACCOUNT_PRODUCT_CODE,
            "INQR_DVSN": "01",
            "CTX_AREA_NK": "",
            "CTX_AREA_FK": "",
            "CTX_AREA_CCD": "",
        }

        raw = self.client.get(config.BALANCE_ENDPOINT, params=params)
        logger.info("Balance response received")

        holdings = []
        available_cash = 0
        total_asset = 0

        output1 = raw.get("output1")
        if isinstance(output1, list) and output1:
            item = output1[0]
            available_cash = int(item.get("dpsl_amt", 0) or item.get("ord_psbl_cash_amt", 0) or 0)
            total_asset = int(item.get("tot_evlu_amt", 0) or item.get("tot_avail_rvse_amt", 0) or 0)

        output2 = raw.get("output2")
        if isinstance(output2, list):
            for item in output2:
                holdings.append(
                    {
                        "symbol": item.get("pdno") or item.get("isu_cd") or "",
                        "quantity": int(item.get("hldg_qty", 0) or item.get("pchs_qty", 0) or 0),
                        "average_price": int(item.get("pchs_avg_pric", 0) or item.get("avg_prc", 0) or 0),
                    }
                )

        return AccountSummary(
            available_cash=available_cash,
            total_asset=total_asset,
            holdings=holdings,
            raw=raw,
        )
