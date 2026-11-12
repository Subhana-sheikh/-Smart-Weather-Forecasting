"""Location geocoding services for OpenWeatherMap and Open-Meteo fallback."""

from __future__ import annotations

from typing import Any

from services.http_client import is_usable_api_key, safe_get_json

OPENWEATHER_GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
OPENMETEO_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"


def _deduplicate_locations(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate locations that share the same name/state/country or coordinates."""
    seen: set[tuple[Any, ...]] = set()
    unique: list[dict[str, Any]] = []
    for loc in items:
        key_name = (
            (loc.get("name") or "").strip().lower(),
            (loc.get("state") or "").strip().lower(),
            (loc.get("country") or "").strip().lower(),
        )
        lat = loc.get("lat")
        lon = loc.get("lon")
        key_coord = (
            round(float(lat), 2) if lat is not None else None,
            round(float(lon), 2) if lon is not None else None,
        )
        if key_name in seen or key_coord in seen:
            continue
        seen.add(key_name)
        seen.add(key_coord)
        unique.append(loc)
    return unique


def _normalize_openweather_locations(raw_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert raw OpenWeather geocoding items into a consistent dictionary schema."""
    normalized: list[dict[str, Any]] = []
    for item in raw_items:
        lat = item.get("lat")
        lon = item.get("lon")
        name = item.get("name")
        if name is None or lat is None or lon is None:
            continue
        local_names = item.get("local_names") or {}
        normalized.append(
            {
                "name": str(name),
                "local_name_hi": local_names.get("hi"),
                "state": str(item.get("state") or "").strip(),
                "country": str(item.get("country") or "").strip(),
                "lat": float(lat),
                "lon": float(lon),
                "provider": "OpenWeatherMap",
            }
        )
    return _deduplicate_locations(normalized)


def _filter_by_state_hint(
    results: list[dict[str, Any]],
    state_hint: str,
) -> list[dict[str, Any]]:
    """Narrow results when the user typed 'City, State' and state matches."""
    if not state_hint:
        return results
    hint = state_hint.strip().lower()
    if hint in {"mp", "m.p.", "m.p"}:
        hint = "madhya pradesh"
    elif hint in {"up", "u.p."}:
        hint = "uttar pradesh"
    elif hint in {"cg", "c.g."}:
        hint = "chhattisgarh"
    elif hint in {"rj", "raj"}:
        hint = "rajasthan"
    elif hint in {"mh"}:
        hint = "maharashtra"
    elif hint in {"hp"}:
        hint = "himachal pradesh"

    matched = [r for r in results if hint in r.get("state", "").lower()]
    return matched or results


def search_locations_openweather(
    query: str,
    api_key: str | None,
    india_only: bool = True,
    limit: int = 5,
) -> dict[str, Any]:
    """Search city or district coordinates using the OpenWeather Geocoding API."""
    clean_query = (query or "").strip()
    if not clean_query:
        return {
            "ok": False,
            "results": [],
            "provider": "OpenWeatherMap",
            "error_code": "empty_query",
            "error_detail": "Please enter a city or district name.",
        }

    if not is_usable_api_key(api_key):
        return {
            "ok": False,
            "results": [],
            "provider": "OpenWeatherMap",
            "error_code": "missing_api_key",
            "error_detail": "OpenWeather API key is not configured.",
        }

    parts = [p.strip() for p in clean_query.split(",") if p.strip()]
    city_part = parts[0]
    state_hint = parts[1] if len(parts) > 1 and parts[1].upper() != "IN" else ""

    candidate_queries: list[str] = []
    if india_only:
        if clean_query.upper().endswith(",IN") or clean_query.upper().endswith(", IN"):
            candidate_queries.append(clean_query)
        elif len(parts) == 1:
            candidate_queries.append(f"{clean_query},IN")
        else:
            candidate_queries.append(f"{city_part},IN")
            candidate_queries.append(clean_query)
    else:
        candidate_queries.append(clean_query)

    last_fetched_at = None
    for q_text in candidate_queries:
        res = safe_get_json(
            OPENWEATHER_GEO_URL,
            params={"q": q_text, "limit": limit, "appid": api_key.strip()},
        )
        if not res["ok"]:
            return {
                "ok": False,
                "results": [],
                "provider": "OpenWeatherMap",
                "error_code": res["error_code"],
                "error_detail": res["error_detail"],
            }

        last_fetched_at = res.get("fetched_at")
        raw_data = res["data"]
        if not isinstance(raw_data, list):
            return {
                "ok": False,
                "results": [],
                "provider": "OpenWeatherMap",
                "error_code": "invalid_response",
                "error_detail": "Unexpected geocoding response structure.",
            }

        normalized = _normalize_openweather_locations(raw_data)
        if india_only:
            normalized = [loc for loc in normalized if loc.get("country", "").upper() == "IN"]
        if state_hint:
            normalized = _filter_by_state_hint(normalized, state_hint)

        if normalized:
            return {
                "ok": True,
                "results": normalized[:limit],
                "provider": "OpenWeatherMap",
                "fetched_at": last_fetched_at,
                "error_code": None,
                "error_detail": None,
            }

    return {
        "ok": False,
        "results": [],
        "provider": "OpenWeatherMap",
        "fetched_at": last_fetched_at,
        "error_code": "location_not_found",
        "error_detail": f"No matching location found for '{clean_query}'.",
    }


def search_locations_openmeteo(
    query: str,
    india_only: bool = True,
    limit: int = 5,
) -> dict[str, Any]:
    """Fallback location search using the Open-Meteo Geocoding API (no key required)."""
    clean_query = (query or "").strip()
    if not clean_query:
        return {
            "ok": False,
            "results": [],
            "provider": "Open-Meteo",
            "error_code": "empty_query",
            "error_detail": "Please enter a city or district name.",
        }

    parts = [p.strip() for p in clean_query.split(",") if p.strip()]
    city_part = parts[0]
    state_hint = parts[1] if len(parts) > 1 and parts[1].upper() != "IN" else ""

    params: dict[str, Any] = {
        "name": city_part,
        "count": 10 if india_only or state_hint else limit,
        "language": "en",
        "format": "json",
    }
    if india_only:
        params["countryCode"] = "IN"

    res = safe_get_json(OPENMETEO_GEO_URL, params=params)
    if not res["ok"]:
        return {
            "ok": False,
            "results": [],
            "provider": "Open-Meteo",
            "error_code": res["error_code"],
            "error_detail": res["error_detail"],
        }

    payload = res["data"]
    raw_results = payload.get("results") if isinstance(payload, dict) else None
    if not raw_results:
        return {
            "ok": False,
            "results": [],
            "provider": "Open-Meteo",
            "fetched_at": res.get("fetched_at"),
            "error_code": "location_not_found",
            "error_detail": f"No matching location found for '{clean_query}'.",
        }

    normalized: list[dict[str, Any]] = []
    for item in raw_results:
        lat = item.get("latitude")
        lon = item.get("longitude")
        name = item.get("name")
        if name is None or lat is None or lon is None:
            continue
        country_code = str(item.get("country_code") or "").strip()
        country_name = str(item.get("country") or "").strip()
        normalized.append(
            {
                "name": str(name),
                "local_name_hi": None,
                "state": str(item.get("admin1") or "").strip(),
                "country": country_code or country_name,
                "lat": float(lat),
                "lon": float(lon),
                "provider": "Open-Meteo",
            }
        )

    normalized = _deduplicate_locations(normalized)
    if india_only:
        normalized = [
            loc
            for loc in normalized
            if loc.get("country", "").upper() in {"IN", "INDIA"}
        ]
    if state_hint:
        normalized = _filter_by_state_hint(normalized, state_hint)

    if not normalized:
        return {
            "ok": False,
            "results": [],
            "provider": "Open-Meteo",
            "fetched_at": res.get("fetched_at"),
            "error_code": "location_not_found",
            "error_detail": f"No matching location found for '{clean_query}'.",
        }

    return {
        "ok": True,
        "results": normalized[:limit],
        "provider": "Open-Meteo",
        "fetched_at": res.get("fetched_at"),
        "error_code": None,
        "error_detail": None,
    }


def format_location_label(loc: dict[str, Any]) -> str:
    """Format a normalized location dictionary into 'Name, State, Country'."""
    parts = [loc.get("name") or ""]
    if loc.get("state"):
        parts.append(loc["state"])
    if loc.get("country"):
        parts.append(loc["country"])
    return ", ".join(p for p in parts if p)

