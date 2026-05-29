from samsung_auto_trader.auth import get_bearer_token
from samsung_auto_trader.api_client import ApiClient
from samsung_auto_trader.account import AccountService
from samsung_auto_trader.logger import configure_logger
from samsung_auto_trader.market_data import MarketDataService
from samsung_auto_trader.orders import OrderService
from samsung_auto_trader.trader import SimpleSamsungTrader
from samsung_auto_trader import config

logger = configure_logger()


def main() -> None:
    logger.info("Starting Samsung Electronics mock trading application")

    token = get_bearer_token()
    client = ApiClient(token)
    account_service = AccountService(client, config.GH_ACCOUNT)
    market_service = MarketDataService(client)
    order_service = OrderService(client, config.GH_ACCOUNT)

    trader = SimpleSamsungTrader(market_service, account_service, order_service)
    trader.run()


if __name__ == "__main__":
    main()
