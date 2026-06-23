import time
from datetime import datetime
import pytz
from typing import Optional

from samsung_auto_trader import config
from samsung_auto_trader.account import AccountService, AccountSummary
from samsung_auto_trader.logger import configure_logger
from samsung_auto_trader.market_data import MarketDataService
from samsung_auto_trader.orders import OrderService

logger = configure_logger()


class SimpleSamsungTrader:
    def __init__(
        self,
        market_service: MarketDataService,
        account_service: AccountService,
        order_service: OrderService,
    ) -> None:
        self.market_service = market_service
        self.account_service = account_service
        self.order_service = order_service

    def _is_trading_window(self, now: datetime) -> bool:
        return config.TRADING_START <= now.time() < config.TRADING_END

    def _log_account_summary(self, summary: AccountSummary, label: str) -> None:
        logger.info(
            "%s available cash=%s total asset=%s holdings=%s",
            label,
            summary.available_cash,
            summary.total_asset,
            summary.holdings,
        )

    def _find_symbol_quantity(self, summary: AccountSummary, symbol: str) -> int:
        for item in summary.holdings:
            if item.get("symbol") == symbol:
                return int(item.get("quantity", 0))
        return 0

    def _check_execution(self, before: AccountSummary, after: AccountSummary, symbol: str, expected_delta: int) -> bool:
        before_qty = self._find_symbol_quantity(before, symbol)
        after_qty = self._find_symbol_quantity(after, symbol)
        logger.info(
            "Execution check for %s: before_qty=%s after_qty=%s expected_delta=%s",
            symbol,
            before_qty,
            after_qty,
            expected_delta,
        )
        return (after_qty - before_qty) == expected_delta

    def _sleep(self, seconds: int) -> None:
        time.sleep(seconds)

    def run(self) -> None:
        logger.info(
            "Trading process started. Window %s to %s",
            config.TRADING_START,
            config.TRADING_END,
        )

        while True:
            now = datetime.now(pytz.timezone("Asia/Seoul"))
            if now.time() >= config.TRADING_END:
                logger.info("Trading window ended at %s. Stopping trader.", now.time())
                break

            if not self._is_trading_window(now):
                logger.info("Waiting for trading window to open. Current time=%s", now.time())
                self._sleep(config.POLL_INTERVAL_SECONDS)
                continue

            current_price = self.market_service.get_current_price(config.TRADING_SYMBOL)
            if current_price is None:
                logger.warning("Skipping loop because market price could not be retrieved")
                self._sleep(config.POLL_INTERVAL_SECONDS)
                continue

            buy_price = max(0, current_price - config.ORDER_PRICE_OFFSET)
            sell_price = current_price + config.ORDER_PRICE_OFFSET
            logger.info("Current price=%s KRW, buy_price=%s KRW, sell_price=%s KRW", current_price, buy_price, sell_price)

            before_summary = self.account_service.get_balance_and_holdings()
            self._log_account_summary(before_summary, "Before orders")

            if before_summary.available_cash >= buy_price and buy_price > 0:
                self.order_service.submit_order(config.TRADING_SYMBOL, "buy", buy_price, 1)
                self._sleep(config.ORDER_CONFIRM_INTERVAL_SECONDS)
                after_buy = self.account_service.get_balance_and_holdings()
                self._log_account_summary(after_buy, "After buy")
                executed = self._check_execution(before_summary, after_buy, config.TRADING_SYMBOL, 1)
                logger.info("Buy execution seems to have occurred: %s", executed)
            else:
                logger.info("Not enough cash to place buy order at %s KRW", buy_price)

            sell_quantity = self._find_symbol_quantity(before_summary, config.TRADING_SYMBOL)
            if sell_quantity > 0:
                self.order_service.submit_order(config.TRADING_SYMBOL, "sell", sell_price, 1)
                self._sleep(config.ORDER_CONFIRM_INTERVAL_SECONDS)
                after_sell = self.account_service.get_balance_and_holdings()
                self._log_account_summary(after_sell, "After sell")
                executed = self._check_execution(before_summary, after_sell, config.TRADING_SYMBOL, -1)
                logger.info("Sell execution seems to have occurred: %s", executed)
            else:
                logger.info("No Samsung Electronics holdings available for sell order")

            self._sleep(config.POLL_INTERVAL_SECONDS)
