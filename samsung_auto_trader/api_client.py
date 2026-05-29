import json
from typing import Any

import requests

from samsung_auto_trader import config
from samsung_auto_trader.logger import configure_logger

logger = configure_logger()


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self, token: str):
        self.base_url = config.BASE_API_URL
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None, json_body: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        last_exception = None

        for attempt in range(1, config.MAX_API_RETRIES + 1):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self.headers,
                    params=params,
                    json=json_body,
                    timeout=config.API_TIMEOUT_SECONDS,
                )
                if response.status_code == 429:
                    logger.warning("Rate limited on %s, attempt %s", path, attempt)
                    continue
                response.raise_for_status()
                if response.text:
                    return response.json()
                return {}
            except requests.RequestException as exc:
                last_exception = exc
                logger.warning(
                    "API request failed %s %s attempt %s: %s",
                    method,
                    path,
                    attempt,
                    exc,
                )
        raise ApiError(f"Failed API request {method} {path}: {last_exception}") from last_exception

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, json_body: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, json_body=json_body)
