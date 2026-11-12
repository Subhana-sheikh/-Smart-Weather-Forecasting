"""Air quality service for OpenWeather Air Pollution API and Open-Meteo fallback."""

from __future__ import annotations

from typing import Any

from services.http_client import format_unix_timestamp, is_usable_api_key, safe_get_json

OPENWEATHER_AQI_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
OPENMETEO_AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def _to_float_or_none(val: Any) -> float | None:
    """Safely convert numeric pollutant concentration to float or None."""
    if val is None:
        return None
    try:
        return round(float(val), 2)
    except (TypeError, ValueError):
        return None


def fetch_air_quality_openweather(
    lat: float,
    lon: float,
    api_key: str | None,
    tz_offset_sec: int | None = None,
) -> dict[str, Any]:
    """Fetch current air pollution data from OpenWeatherMap (1-5 AQI scale)."""
    if not is_usable_api_key(api_key):
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": "missing_api_key",
            "error_detail": "OpenWeather API key is not configured.",
        }

    res = safe_get_json(
        OPENWEATHER_AQI_URL,
        params={"lat": lat, "lon": lon, "appid": api_key.strip()},
    )
    if not res["ok"]:
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": res["error_code"],
            "error_detail": res["error_detail"],
        }

    payload = res["data"]
    items = payload.get("list") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items:
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": "invalid_response",
            "error_detail": "Air pollution API returned no observations.",
        }

    entry = items[0] if isinstance(items[0], dict) else {}
    main_block = entry.get("main") or {}
    comp = entry.get("components") or {}

    aqi_val = main_block.get("aqi")
    try:
        aqi_int = int(aqi_val) if aqi_val is not None else None
    except (TypeError, ValueError):
        aqi_int = None

    return {
        "ok": True,
        "provider": "OpenWeatherMap",
        "scale_type": "openweather_1_to_5",
        "fetched_at": res.get("fetched_at"),
        "error_code": None,
        "error_detail": None,
        "data": {
            "aqi": aqi_int,
            "observation_time": format_unix_timestamp(entry.get("dt"), tz_offset_sec),
            "pm2_5": _to_float_or_none(comp.get("pm2_5")),
            "pm10": _to_float_or_none(comp.get("pm10")),
            "no2": _to_float_or_none(comp.get("no2")),
            "o3": _to_float_or_none(comp.get("o3")),
            "so2": _to_float_or_none(comp.get("so2")),
            "co": _to_float_or_none(comp.get("co")),
        },
    }


def fetch_air_quality_openmeteo(lat: float, lon: float) -> dict[str, Any]:
    """Fallback air quality fetch via Open-Meteo (European AQI scale, not 1-5)."""
    res = safe_get_json(
        OPENMETEO_AQI_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": (
                "european_aqi,pm2_5,pm10,nitrogen_dioxide,"
                "ozone,sulphur_dioxide,carbon_monoxide"
            ),
            "timezone": "auto",
        },
    )
    if not res["ok"]:
        return {
            "ok": False,
            "provider": "Open-Meteo (Fallback)",
            "error_code": res["error_code"],
            "error_detail": res["error_detail"],
        }

    payload = res["data"]
    current = payload.get("current") if isinstance(payload, dict) else None
    if not isinstance(current, dict) or not current:
        return {
            "ok": False,
            "provider": "Open-Meteo (Fallback)",
            "error_code": "invalid_response",
            "error_detail": "Open-Meteo air quality response had no current data.",
        }

    eaqi_raw = current.get("european_aqi")
    try:
        eaqi_val = int(round(float(eaqi_raw))) if eaqi_raw is not None else None
    except (TypeError, ValueError):
        eaqi_val = None

    return {
        "ok": True,
        "provider": "Open-Meteo (Fallback)",
        "scale_type": "openmeteo_european_aqi",
        "fetched_at": res.get("fetched_at"),
        "error_code": None,
        "error_detail": None,
        "data": {
            "aqi": eaqi_val,
            "observation_time": current.get("time"),
            "pm2_5": _to_float_or_none(current.get("pm2_5")),
            "pm10": _to_float_or_none(current.get("pm10")),
            "no2": _to_float_or_none(current.get("nitrogen_dioxide")),
            "o3": _to_float_or_none(current.get("ozone")),
            "so2": _to_float_or_none(current.get("sulphur_dioxide")),
            "co": _to_float_or_none(current.get("carbon_monoxide")),
        },
    }

