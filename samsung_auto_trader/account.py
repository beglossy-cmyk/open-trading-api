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
            "CANO": self.account_no,
            "ACNT_PRDT_CD": config.ACCOUNT_PRODUCT_CODE,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "N",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        self.client.headers["tr_id"] = "VTTC8434R"
        raw = self.client.get(config.BALANCE_ENDPOINT, params=params)
        logger.info("Balance response received: rt_cd=%s", raw.get("rt_cd"))

        available_cash = 0
        total_asset = 0
        holdings = []

        output2 = raw.get("output2")
        if isinstance(output2, list) and output2:
            item = output2[0]
            available_cash = int(item.get("dnca_tot_amt", 0) or 0)
            total_asset = int(item.get("tot_evlu_amt", 0) or 0)

        output1 = raw.get("output1")
        if isinstance(output1, list):
            for item in output1:
                qty = int(item.get("hldg_qty", 0) or 0)
                if qty > 0:
                    holdings.append({
                        "symbol": item.get("pdno", ""),
                        "quantity": qty,
                        "average_price": int(float(item.get("pchs_avg_pric", 0) or 0)),
                    })

        return AccountSummary(
            available_cash=available_cash,
            total_asset=total_asset,
            holdings=holdings,
            raw=raw,
        )
