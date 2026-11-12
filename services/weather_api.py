"""Weather and five-day forecast clients (OpenWeatherMap primary + Open-Meteo fallback)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from services.http_client import (
    format_unix_timestamp,
    get_local_tz,
    is_usable_api_key,
    safe_get_json,
)

OPENWEATHER_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
OPENMETEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WMO_WEATHER_DESCRIPTIONS: dict[int, tuple[str, str]] = {
    0: ("clear sky", "☀️"),
    1: ("mainly clear", "🌤️"),
    2: ("partly cloudy", "⛅"),
    3: ("overcast clouds", "☁️"),
    45: ("fog", "🌫️"),
    48: ("depositing rime fog", "🌫️"),
    51: ("light drizzle", "🌦️"),
    53: ("moderate drizzle", "🌦️"),
    55: ("dense drizzle", "🌧️"),
    56: ("light freezing drizzle", "🌧️"),
    57: ("dense freezing drizzle", "🌧️"),
    61: ("light rain", "🌦️"),
    63: ("moderate rain", "🌧️"),
    65: ("heavy intensity rain", "🌧️"),
    66: ("light freezing rain", "🌧️"),
    67: ("heavy freezing rain", "🌧️"),
    71: ("light snow", "🌨️"),
    73: ("moderate snow", "🌨️"),
    75: ("heavy snow", "❄️"),
    77: ("snow grains", "❄️"),
    80: ("light rain showers", "🌦️"),
    81: ("moderate rain showers", "🌧️"),
    82: ("violent rain showers", "⛈️"),
    85: ("light snow showers", "🌨️"),
    86: ("heavy snow showers", "❄️"),
    95: ("thunderstorm", "⛈️"),
    96: ("thunderstorm with slight hail", "⛈️"),
    99: ("thunderstorm with heavy hail", "⛈️"),
}


def weather_emoji_from_icon_or_main(icon_code: str | None, weather_main: str | None) -> str:
    """Return a clean weather emoji matching OpenWeather icon code or condition category."""
    if icon_code:
        prefix = icon_code[:2]
        mapping = {
            "01": "☀️" if icon_code.endswith("d") else "🌙",
            "02": "🌤️" if icon_code.endswith("d") else "☁️",
            "03": "⛅",
            "04": "☁️",
            "09": "🌧️",
            "10": "🌦️",
            "11": "⛈️",
            "13": "❄️",
            "50": "🌫️",
        }
        if prefix in mapping:
            return mapping[prefix]

    main_lower = (weather_main or "").lower()
    if "thunder" in main_lower:
        return "⛈️"
    if "rain" in main_lower or "drizzle" in main_lower:
        return "🌧️"
    if "cloud" in main_lower:
        return "☁️"
    if "clear" in main_lower:
        return "☀️"
    if any(k in main_lower for k in ("mist", "fog", "haze", "smoke", "dust")):
        return "🌫️"
    return "🌡️"


def _to_float_or_none(val: Any) -> float | None:
    """Safely convert numeric field to float while preserving missingness as None."""
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _ms_to_kmh(speed_ms: Any) -> float | None:
    """Convert OpenWeather wind speed from metres/second to km/h."""
    val = _to_float_or_none(speed_ms)
    if val is None:
        return None
    return round(val * 3.6, 1)


def fetch_current_weather_openweather(
    lat: float,
    lon: float,
    api_key: str | None,
) -> dict[str, Any]:
    """Fetch current weather from OpenWeather /data/2.5/weather using metric units."""
    if not is_usable_api_key(api_key):
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": "missing_api_key",
            "error_detail": "OpenWeather API key is not configured.",
        }

    res = safe_get_json(
        OPENWEATHER_CURRENT_URL,
        params={"lat": lat, "lon": lon, "appid": api_key.strip(), "units": "metric"},
    )
    if not res["ok"]:
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": res["error_code"],
            "error_detail": res["error_detail"],
        }

    data = res["data"]
    if not isinstance(data, dict) or "main" not in data:
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": "invalid_response",
            "error_detail": "Current weather response did not include expected weather fields.",
        }

    main_block = data.get("main") or {}
    wind_block = data.get("wind") or {}
    clouds_block = data.get("clouds") or {}
    sys_block = data.get("sys") or {}
    weather_list = data.get("weather") or []
    weather_item = weather_list[0] if weather_list and isinstance(weather_list[0], dict) else {}

    tz_offset = data.get("timezone")
    icon_code = weather_item.get("icon")
    weather_main = weather_item.get("main")

    return {
        "ok": True,
        "provider": "OpenWeatherMap",
        "fetched_at": res.get("fetched_at"),
        "error_code": None,
        "error_detail": None,
        "data": {
            "temp_c": _to_float_or_none(main_block.get("temp")),
            "feels_like_c": _to_float_or_none(main_block.get("feels_like")),
            "humidity_pct": _to_float_or_none(main_block.get("humidity")),
            "pressure_hpa": _to_float_or_none(main_block.get("pressure")),
            "wind_speed_kmh": _ms_to_kmh(wind_block.get("speed")),
            "clouds_pct": _to_float_or_none(clouds_block.get("all")),
            "weather_main": weather_main,
            "weather_desc": weather_item.get("description"),
            "weather_icon_code": icon_code,
            "weather_icon_url": (
                f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
                if icon_code
                else None
            ),
            "weather_emoji": weather_emoji_from_icon_or_main(icon_code, weather_main),
            "observation_time": format_unix_timestamp(data.get("dt"), tz_offset),
            "sunrise_time": format_unix_timestamp(sys_block.get("sunrise"), tz_offset, "%I:%M %p"),
            "sunset_time": format_unix_timestamp(sys_block.get("sunset"), tz_offset, "%I:%M %p"),
            "station_name": data.get("name"),
            "timezone_offset_sec": tz_offset,
        },
    }


def fetch_forecast_openweather(
    lat: float,
    lon: float,
    api_key: str | None,
) -> dict[str, Any]:
    """Fetch five-day / three-hour forecast from OpenWeather /data/2.5/forecast."""
    if not is_usable_api_key(api_key):
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": "missing_api_key",
            "error_detail": "OpenWeather API key is not configured.",
        }

    res = safe_get_json(
        OPENWEATHER_FORECAST_URL,
        params={"lat": lat, "lon": lon, "appid": api_key.strip(), "units": "metric"},
    )
    if not res["ok"]:
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": res["error_code"],
            "error_detail": res["error_detail"],
        }

    data = res["data"]
    raw_list = data.get("list") if isinstance(data, dict) else None
    if not isinstance(raw_list, list) or not raw_list:
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": "invalid_response",
            "error_detail": "Forecast response contained no forecast intervals.",
        }

    city_info = data.get("city") or {}
    tz_offset = city_info.get("timezone")
    local_tz = get_local_tz(tz_offset)

    intervals: list[dict[str, Any]] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        dt_unix = item.get("dt")
        if dt_unix is None:
            continue
        local_dt = datetime.fromtimestamp(float(dt_unix), tz=timezone.utc).astimezone(local_tz)
        main_block = item.get("main") or {}
        wind_block = item.get("wind") or {}
        weather_list = item.get("weather") or []
        weather_item = weather_list[0] if weather_list and isinstance(weather_list[0], dict) else {}

        pop_raw = _to_float_or_none(item.get("pop"))
        rain_prob_pct = round(pop_raw * 100.0, 1) if pop_raw is not None else None
        icon_code = weather_item.get("icon")
        weather_main = weather_item.get("main")

        intervals.append(
            {
                "dt_unix": int(dt_unix),
                "local_dt": local_dt,
                "local_date": local_dt.date(),
                "local_time_str": local_dt.strftime("%d %b, %I:%M %p"),
                "temp_c": _to_float_or_none(main_block.get("temp")),
                "temp_min_c": _to_float_or_none(main_block.get("temp_min")),
                "temp_max_c": _to_float_or_none(main_block.get("temp_max")),
                "humidity_pct": _to_float_or_none(main_block.get("humidity")),
                "wind_speed_kmh": _ms_to_kmh(wind_block.get("speed")),
                "rain_prob_pct": rain_prob_pct,
                "weather_main": weather_main,
                "weather_desc": weather_item.get("description"),
                "weather_icon_code": icon_code,
                "weather_emoji": weather_emoji_from_icon_or_main(icon_code, weather_main),
            }
        )

    if not intervals:
        return {
            "ok": False,
            "provider": "OpenWeatherMap",
            "error_code": "invalid_response",
            "error_detail": "No valid forecast intervals could be parsed.",
        }

    daily_df = summarize_daily_forecast(intervals, max_days=5)
    return {
        "ok": True,
        "provider": "OpenWeatherMap",
        "interval_label": "3-hour",
        "fetched_at": res.get("fetched_at"),
        "error_code": None,
        "error_detail": None,
        "intervals": intervals,
        "daily_df": daily_df,
    }


def fetch_weather_bundle_openmeteo(lat: float, lon: float) -> dict[str, Any]:
    """Fetch current weather and five-day forecast from Open-Meteo (optional fallback)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "pressure_msl,cloud_cover,wind_speed_10m,weather_code,is_day"
        ),
        "hourly": "temperature_2m,precipitation_probability,wind_speed_10m,weather_code",
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,wind_speed_10m_max,sunrise,sunset"
        ),
        "wind_speed_unit": "kmh",
        "timezone": "auto",
        "forecast_days": 5,
    }
    res = safe_get_json(OPENMETEO_FORECAST_URL, params=params)
    if not res["ok"]:
        return {
            "current": {
                "ok": False,
                "provider": "Open-Meteo (Fallback)",
                "error_code": res["error_code"],
                "error_detail": res["error_detail"],
            },
            "forecast": {
                "ok": False,
                "provider": "Open-Meteo (Fallback)",
                "error_code": res["error_code"],
                "error_detail": res["error_detail"],
            },
        }

    payload = res["data"]
    if not isinstance(payload, dict):
        err = {
            "ok": False,
            "provider": "Open-Meteo (Fallback)",
            "error_code": "invalid_response",
            "error_detail": "Open-Meteo returned invalid data format.",
        }
        return {"current": err, "forecast": err}

    fetched_at = res.get("fetched_at")
    current_raw = payload.get("current") or {}
    daily_raw = payload.get("daily") or {}
    hourly_raw = payload.get("hourly") or {}

    wmo_code = current_raw.get("weather_code")
    wmo_desc, wmo_emoji = WMO_WEATHER_DESCRIPTIONS.get(
        int(wmo_code) if wmo_code is not None else -1,
        (f"weather code {wmo_code}" if wmo_code is not None else None, "🌤️"),
    )
    if wmo_code == 0 and current_raw.get("is_day") == 0:
        wmo_emoji = "🌙"

    obs_time_iso = current_raw.get("time")
    obs_time_fmt = _format_iso_datetime(obs_time_iso, "%d %b %Y, %I:%M %p")

    sunrise_list = daily_raw.get("sunrise") or []
    sunset_list = daily_raw.get("sunset") or []
    sunrise_fmt = _format_iso_datetime(sunrise_list[0], "%I:%M %p") if sunrise_list else None
    sunset_fmt = _format_iso_datetime(sunset_list[0], "%I:%M %p") if sunset_list else None

    current_result = {
        "ok": bool(current_raw),
        "provider": "Open-Meteo (Fallback)",
        "fetched_at": fetched_at,
        "error_code": None if current_raw else "invalid_response",
        "error_detail": None if current_raw else "Current weather missing in Open-Meteo response.",
        "data": {
            "temp_c": _to_float_or_none(current_raw.get("temperature_2m")),
            "feels_like_c": _to_float_or_none(current_raw.get("apparent_temperature")),
            "humidity_pct": _to_float_or_none(current_raw.get("relative_humidity_2m")),
            "pressure_hpa": _to_float_or_none(current_raw.get("pressure_msl")),
            "wind_speed_kmh": _to_float_or_none(current_raw.get("wind_speed_10m")),
            "clouds_pct": _to_float_or_none(current_raw.get("cloud_cover")),
            "weather_main": wmo_desc,
            "weather_desc": wmo_desc,
            "weather_icon_code": None,
            "weather_icon_url": None,
            "weather_emoji": wmo_emoji,
            "observation_time": obs_time_fmt or obs_time_iso,
            "sunrise_time": sunrise_fmt,
            "sunset_time": sunset_fmt,
            "station_name": None,
            "timezone_offset_sec": payload.get("utc_offset_seconds"),
        },
    }

    # Build hourly intervals from Open-Meteo for transparent advisory rules
    intervals: list[dict[str, Any]] = []
    h_times = hourly_raw.get("time") or []
    h_temps = hourly_raw.get("temperature_2m") or []
    h_pops = hourly_raw.get("precipitation_probability") or []
    h_winds = hourly_raw.get("wind_speed_10m") or []
    h_codes = hourly_raw.get("weather_code") or []

    # Filter intervals from current observation time forward when available
    now_ref = None
    if obs_time_iso:
        try:
            now_ref = datetime.fromisoformat(obs_time_iso)
        except ValueError:
            now_ref = None

    for idx, t_str in enumerate(h_times):
        try:
            local_dt = datetime.fromisoformat(t_str)
        except ValueError:
            continue
        if now_ref is not None and local_dt < now_ref:
            continue
        code_val = h_codes[idx] if idx < len(h_codes) else None
        desc_i, emoji_i = WMO_WEATHER_DESCRIPTIONS.get(
            int(code_val) if code_val is not None else -1,
            (f"weather code {code_val}" if code_val is not None else None, "🌤️"),
        )
        t_val = _to_float_or_none(h_temps[idx]) if idx < len(h_temps) else None
        intervals.append(
            {
                "dt_unix": int(local_dt.timestamp()),
                "local_dt": local_dt,
                "local_date": local_dt.date(),
                "local_time_str": local_dt.strftime("%d %b, %I:%M %p"),
                "temp_c": t_val,
                "temp_min_c": t_val,
                "temp_max_c": t_val,
                "humidity_pct": None,
                "wind_speed_kmh": _to_float_or_none(h_winds[idx]) if idx < len(h_winds) else None,
                "rain_prob_pct": _to_float_or_none(h_pops[idx]) if idx < len(h_pops) else None,
                "weather_main": desc_i,
                "weather_desc": desc_i,
                "weather_icon_code": None,
                "weather_emoji": emoji_i,
            }
        )

    # Build daily forecast directly from Open-Meteo daily fields (never invent missing dates)
    d_dates = daily_raw.get("time") or []
    d_tmax = daily_raw.get("temperature_2m_max") or []
    d_tmin = daily_raw.get("temperature_2m_min") or []
    d_pop = daily_raw.get("precipitation_probability_max") or []
    d_wind = daily_raw.get("wind_speed_10m_max") or []
    d_codes = daily_raw.get("weather_code") or []

    daily_rows: list[dict[str, Any]] = []
    for idx, d_str in enumerate(d_dates[:5]):
        try:
            d_obj = datetime.fromisoformat(d_str).date()
        except ValueError:
            continue
        code_val = d_codes[idx] if idx < len(d_codes) else None
        desc_d, emoji_d = WMO_WEATHER_DESCRIPTIONS.get(
            int(code_val) if code_val is not None else -1,
            (f"weather code {code_val}" if code_val is not None else None, "🌤️"),
        )
        daily_rows.append(
            {
                "date": d_obj,
                "date_str": d_obj.strftime("%d %b"),
                "weekday_short": d_obj.strftime("%a"),
                "temp_min_c": _to_float_or_none(d_tmin[idx]) if idx < len(d_tmin) else None,
                "temp_max_c": _to_float_or_none(d_tmax[idx]) if idx < len(d_tmax) else None,
                "max_rain_prob_pct": _to_float_or_none(d_pop[idx]) if idx < len(d_pop) else None,
                "max_wind_kmh": _to_float_or_none(d_wind[idx]) if idx < len(d_wind) else None,
                "condition_desc": desc_d,
                "weather_emoji": emoji_d,
                "weather_icon_url": None,
                "interval_count": None,
            }
        )

    daily_df = pd.DataFrame(daily_rows)
    forecast_ok = bool(not daily_df.empty and intervals)
    forecast_result = {
        "ok": forecast_ok,
        "provider": "Open-Meteo (Fallback)",
        "interval_label": "hourly",
        "fetched_at": fetched_at,
        "error_code": None if forecast_ok else "invalid_response",
        "error_detail": None if forecast_ok else "Forecast data unavailable from Open-Meteo.",
        "intervals": intervals,
        "daily_df": daily_df,
    }
    return {"current": current_result, "forecast": forecast_result}


def _format_iso_datetime(iso_text: str | None, fmt: str) -> str | None:
    """Safely format an ISO datetime string returned by Open-Meteo."""
    if not iso_text:
        return None
    try:
        return datetime.fromisoformat(iso_text).strftime(fmt)
    except ValueError:
        return iso_text


def summarize_daily_forecast(intervals: list[dict[str, Any]], max_days: int = 5) -> pd.DataFrame:
    """Aggregate 3-hour forecast intervals into daily summaries using pandas without inventing values."""
    if not intervals:
        return pd.DataFrame()

    df = pd.DataFrame(intervals)
    # Build effective min/max per interval using only available temperature fields
    df["effective_min"] = df["temp_min_c"].combine_first(df["temp_c"])
    df["effective_max"] = df["temp_max_c"].combine_first(df["temp_c"])

    daily_rows: list[dict[str, Any]] = []
    for date_val, group in df.groupby("local_date", sort=True):
        min_series = group["effective_min"].dropna()
        max_series = group["effective_max"].dropna()
        pop_series = group["rain_prob_pct"].dropna()
        wind_series = group["wind_speed_kmh"].dropna()

        rep_row = _select_representative_interval(group)
        icon_code = rep_row.get("weather_icon_code")

        daily_rows.append(
            {
                "date": date_val,
                "date_str": date_val.strftime("%d %b"),
                "weekday_short": date_val.strftime("%a"),
                "temp_min_c": round(float(min_series.min()), 1) if not min_series.empty else None,
                "temp_max_c": round(float(max_series.max()), 1) if not max_series.empty else None,
                "max_rain_prob_pct": (
                    round(float(pop_series.max()), 0) if not pop_series.empty else None
                ),
                "max_wind_kmh": (
                    round(float(wind_series.max()), 1) if not wind_series.empty else None
                ),
                "condition_desc": rep_row.get("weather_desc"),
                "weather_emoji": rep_row.get("weather_emoji") or "🌤️",
                "weather_icon_url": (
                    f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
                    if icon_code
                    else None
                ),
                "interval_count": int(len(group)),
            }
        )

    result_df = pd.DataFrame(daily_rows)
    if max_days and len(result_df) > max_days:
        result_df = result_df.head(max_days).reset_index(drop=True)
    return result_df


def _select_representative_interval(day_group: pd.DataFrame) -> dict[str, Any]:
    """Pick a midday interval (closest to 12:00-15:00 local) for representative daily condition."""
    if day_group.empty:
        return {}
    try:
        hours = day_group["local_dt"].apply(lambda dt: abs(dt.hour - 13))
        idx = hours.idxmin()
        return day_group.loc[idx].to_dict()
    except Exception:
        return day_group.iloc[0].to_dict()

