import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from samsung_auto_trader import config
from samsung_auto_trader.logger import configure_logger

logger = configure_logger()


class AuthError(Exception):
    pass


def _today_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _load_token_cache(path: Path) -> Optional[str]:
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as fp:
            payload = json.load(fp)
        if payload.get("date") == _today_date() and payload.get("token"):
            logger.info("Reusing cached token for today")
            return payload["token"]
    except Exception as exc:
        logger.warning("Failed to read token cache: %s", exc)
    return None


def _save_token_cache(path: Path, token: str) -> None:
    payload = {"token": token, "date": _today_date()}
    try:
        with path.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp)
        logger.info("Saved token cache for today")
    except Exception as exc:
        logger.warning("Failed to write token cache: %s", exc)


def _validate_credentials() -> tuple[str, str, str]:
    if not config.GH_APPKEY or not config.GH_APPSECRET or not config.GH_ACCOUNT:
        raise AuthError(
            "Required environment variables missing: GH_APPKEY, GH_APPSECRET, GH_ACCOUNT"
        )
    return config.GH_APPKEY, config.GH_APPSECRET, config.GH_ACCOUNT


def get_bearer_token() -> str:
    cached_token = _load_token_cache(config.TOKEN_CACHE_PATH)
    if cached_token:
        return cached_token

    appkey, appsecret, _account = _validate_credentials()
    token_url = f"{config.BASE_API_URL}{config.TOKEN_ENDPOINT}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "appsecret": appsecret,
    }

    try:
        response = requests.post(
            token_url,
            headers=headers,
            data=data,
            timeout=config.API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body = response.json()
        token = body.get("access_token") or body.get("accessToken")
        if not token:
            raise AuthError("Token response did not contain access_token")
        logger.info("Fetched new token from auth endpoint")
        _save_token_cache(config.TOKEN_CACHE_PATH, token)
        return token
    except requests.RequestException as exc:
        raise AuthError(f"Failed to fetch token: {exc}") from exc
