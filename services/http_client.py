"""Shared HTTP request handling, API key resolution, and time utilities."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests
from dotenv import dotenv_values

ENV_FILE_PATH = Path(__file__).resolve().parent.parent / ".env"

IST_ZONE = ZoneInfo("Asia/Kolkata")
PLACEHOLDER_KEYS = {
    "",
    "PASTE_YOUR_OWN_KEY_HERE",
    "YOUR_API_KEY",
    "YOUR_API_KEY_HERE",
    "REPLACE_ME",
}
DEFAULT_TIMEOUT_SEC = 12


def is_usable_api_key(key: str | None) -> bool:
    """Return True when an API key string is present and not a placeholder."""
    if not key or not isinstance(key, str):
        return False
    cleaned = key.strip()
    return cleaned not in PLACEHOLDER_KEYS and len(cleaned) >= 8


def resolve_openweather_api_key(session_key: str | None = None) -> tuple[str | None, str]:
    """Resolve OpenWeather API key from session input, environment, .env file, or Streamlit secrets."""
    if is_usable_api_key(session_key):
        return session_key.strip(), "session"

    env_key = os.getenv("OPENWEATHER_API_KEY")
    if is_usable_api_key(env_key):
        return env_key.strip(), "env"

    if ENV_FILE_PATH.exists():
        file_values = dotenv_values(ENV_FILE_PATH)
        dotenv_key = file_values.get("OPENWEATHER_API_KEY")
        if is_usable_api_key(dotenv_key):
            return str(dotenv_key).strip(), ".env"

    try:
        import streamlit as st

        secret_key = st.secrets.get("OPENWEATHER_API_KEY")
        if is_usable_api_key(secret_key):
            return str(secret_key).strip(), "secrets"
    except Exception:
        # Secrets may not exist locally or code may run outside Streamlit (e.g. unit tests).
        pass

    return None, "missing"


def current_ist_timestamp_str() -> str:
    """Return the current timestamp formatted in IST for UI update tracking."""
    return datetime.now(IST_ZONE).strftime("%d %b %Y, %I:%M:%S %p IST")


def get_local_tz(tz_offset_sec: int | None) -> timezone | ZoneInfo:
    """Build a tzinfo object from a UTC offset in seconds, defaulting to IST."""
    if tz_offset_sec is not None:
        return timezone(timedelta(seconds=int(tz_offset_sec)))
    return IST_ZONE


def format_unix_timestamp(
    unix_ts: int | float | None,
    tz_offset_sec: int | None = None,
    fmt: str = "%d %b %Y, %I:%M %p",
) -> str | None:
    """Convert a Unix timestamp to a formatted local time string."""
    if unix_ts is None:
        return None
    try:
        tz = get_local_tz(tz_offset_sec)
        dt = datetime.fromtimestamp(float(unix_ts), tz=timezone.utc).astimezone(tz)
        return dt.strftime(fmt)
    except (TypeError, ValueError, OSError):
        return None


def safe_get_json(
    url: str,
    params: dict[str, Any],
    timeout: int = DEFAULT_TIMEOUT_SEC,
) -> dict[str, Any]:
    """Perform a GET request and return structured JSON or a sanitized error payload."""
    try:
        response = requests.get(url, params=params, timeout=timeout)
    except requests.Timeout:
        return {
            "ok": False,
            "error_code": "timeout",
            "error_detail": "Request timed out while contacting the weather provider.",
            "status_code": None,
        }
    except requests.ConnectionError:
        return {
            "ok": False,
            "error_code": "network_error",
            "error_detail": "Could not connect to the weather provider. Check internet access.",
            "status_code": None,
        }
    except requests.RequestException as exc:
        # Never expose full request URL because it can contain appid query parameter.
        return {
            "ok": False,
            "error_code": "request_error",
            "error_detail": f"HTTP client error: {type(exc).__name__}",
            "status_code": None,
        }

    status = response.status_code
    if status == 401:
        return {
            "ok": False,
            "error_code": "invalid_api_key",
            "error_detail": "OpenWeather rejected the API key (HTTP 401). Newly created keys can take a short time to activate.",
            "status_code": status,
        }
    if status == 429:
        return {
            "ok": False,
            "error_code": "rate_limit",
            "error_detail": "API rate limit reached (HTTP 429). Please wait and try again.",
            "status_code": status,
        }
    if status == 404:
        return {
            "ok": False,
            "error_code": "not_found",
            "error_detail": "Requested location or resource was not found (HTTP 404).",
            "status_code": status,
        }
    if status >= 400:
        provider_msg = ""
        try:
            err_json = response.json()
            if isinstance(err_json, dict) and err_json.get("message"):
                provider_msg = str(err_json["message"])
        except ValueError:
            provider_msg = ""
        detail = f"Provider returned HTTP {status}"
        if provider_msg:
            detail = f"{detail}: {provider_msg}"
        return {
            "ok": False,
            "error_code": "api_error",
            "error_detail": detail,
            "status_code": status,
        }

    try:
        payload = response.json()
    except ValueError:
        return {
            "ok": False,
            "error_code": "invalid_response",
            "error_detail": "Weather provider returned non-JSON data.",
            "status_code": status,
        }

    return {
        "ok": True,
        "data": payload,
        "fetched_at": current_ist_timestamp_str(),
    }

