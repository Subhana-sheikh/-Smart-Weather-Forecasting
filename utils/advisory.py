"""Transparent rule-based agriculture advisory generator from live forecast intervals."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

RAIN_PROB_HIGH_THRESHOLD = 70.0
RAIN_PROB_LOW_THRESHOLD = 30.0
TEMP_HIGH_THRESHOLD_C = 40.0
WIND_HIGH_THRESHOLD_KMH = 20.0


def filter_intervals_by_horizon(
    intervals: list[dict[str, Any]],
    horizon_hours: int | None = None,
) -> list[dict[str, Any]]:
    """Slice forecast intervals to the requested future horizon (e.g. 24h, 48h, or full 5-day)."""
    if not intervals or horizon_hours is None:
        return list(intervals)

    first_dt = intervals[0].get("local_dt")
    if first_dt is None:
        return list(intervals)

    cutoff = first_dt + timedelta(hours=horizon_hours)
    return [item for item in intervals if item.get("local_dt") and item["local_dt"] <= cutoff]


def generate_agriculture_advisories(
    intervals: list[dict[str, Any]],
    horizon_hours: int | None = None,
    lang: str = "en",
) -> dict[str, Any]:
    """Evaluate transparent if/else agriculture rules against actual forecast intervals."""
    scoped = filter_intervals_by_horizon(intervals, horizon_hours=horizon_hours)
    if not scoped:
        return {
            "advisories": [
                {
                    "rule_id": "insufficient_forecast_data",
                    "severity": "info",
                    "title": "अपर्याप्त पूर्वानुमान डेटा" if lang == "hi" else "Insufficient forecast data",
                    "message": (
                        "कृषि सलाह बनाने के लिए पर्याप्त पूर्वानुमान डेटा उपलब्ध नहीं है।"
                        if lang == "hi"
                        else "Insufficient forecast data is available to generate rule-based advisories."
                    ),
                    "reason": (
                        "पूर्वानुमान अंतराल (intervals) प्राप्त नहीं हुए।"
                        if lang == "hi"
                        else "No forecast intervals were returned by the weather provider."
                    ),
                }
            ],
            "summary": {
                "interval_count": 0,
                "max_rain_prob_pct": None,
                "max_temp_c": None,
                "max_wind_kmh": None,
            },
        }

    rain_points = [
        (item, item["rain_prob_pct"])
        for item in scoped
        if item.get("rain_prob_pct") is not None
    ]
    temp_points = [
        (
            item,
            item["temp_max_c"] if item.get("temp_max_c") is not None else item.get("temp_c"),
        )
        for item in scoped
        if (item.get("temp_max_c") is not None or item.get("temp_c") is not None)
    ]
    wind_points = [
        (item, item["wind_speed_kmh"])
        for item in scoped
        if item.get("wind_speed_kmh") is not None
    ]

    max_rain_item, max_rain = (
        max(rain_points, key=lambda pair: pair[1]) if rain_points else (None, None)
    )
    max_temp_item, max_temp = (
        max(temp_points, key=lambda pair: pair[1]) if temp_points else (None, None)
    )
    max_wind_item, max_wind = (
        max(wind_points, key=lambda pair: pair[1]) if wind_points else (None, None)
    )

    advisories: list[dict[str, str]] = []

    # Rule 1: Rain probability >= 70%
    if max_rain is None:
        advisories.append(
            {
                "rule_id": "rain_data_missing",
                "severity": "info",
                "title": "बारिश संभावना डेटा उपलब्ध नहीं" if lang == "hi" else "Insufficient forecast data",
                "message": (
                    "बारिश की संभावना का डेटा उपलब्ध नहीं है, इसलिए वर्षा-आधारित सलाह लागू नहीं की गई।"
                    if lang == "hi"
                    else "Insufficient forecast data: rain probability was not provided by the API."
                ),
                "reason": "Missing field: rain probability (pop)" if lang == "en" else "अनुपलब्ध डेटा: बारिश की संभावना (pop)",
            }
        )
    elif max_rain >= RAIN_PROB_HIGH_THRESHOLD:
        peak_time = max_rain_item.get("local_time_str", "")
        advisories.append(
            {
                "rule_id": "high_rain_probability",
                "severity": "warning",
                "title": "अधिक बारिश की संभावना" if lang == "hi" else "High Rain Probability Caution",
                "message": (
                    "बारिश की संभावना अधिक है। दवा का छिड़काव करने से पहले स्थानीय मौसम अपडेट देखें; बारिश से छिड़काव प्रभावित हो सकता है।"
                    if lang == "hi"
                    else "High probability of rain in the forecast. Check local weather updates before spraying; rain may wash off or reduce spraying effectiveness."
                ),
                "reason": (
                    f"बारिश की संभावना: {max_rain:.0f}% (अधिकतम {peak_time} के आसपास) | नियम: >= {RAIN_PROB_HIGH_THRESHOLD:.0f}%"
                    if lang == "hi"
                    else f"Rain probability: {max_rain:.0f}% (peak around {peak_time}) | Rule: >= {RAIN_PROB_HIGH_THRESHOLD:.0f}%"
                ),
            }
        )

    # Rule 2: Forecast maximum temperature > 40°C
    if max_temp is None:
        advisories.append(
            {
                "rule_id": "temp_data_missing",
                "severity": "info",
                "title": "तापमान डेटा अपर्याप्त" if lang == "hi" else "Insufficient forecast data",
                "message": (
                    "तापमान पूर्वानुमान डेटा उपलब्ध नहीं है, इसलिए गर्मी नियम लागू नहीं किया गया।"
                    if lang == "hi"
                    else "Insufficient forecast data: forecast temperature was not provided."
                ),
                "reason": "Missing field: forecast temperature" if lang == "en" else "अनुपलब्ध डेटा: तापमान पूर्वानुमान",
            }
        )
    elif max_temp > TEMP_HIGH_THRESHOLD_C:
        peak_time = max_temp_item.get("local_time_str", "")
        advisories.append(
            {
                "rule_id": "high_temperature",
                "severity": "danger",
                "title": "अधिक तापमान चेतावनी" if lang == "hi" else "High Temperature Caution",
                "message": (
                    "गर्मी अधिक रहने की संभावना है। फसल की जरूरत और स्थानीय कृषि सलाह के अनुसार सुबह या शाम सिंचाई पर विचार करें।"
                    if lang == "hi"
                    else "High temperatures expected. Consider early morning or evening irrigation according to crop needs and local agricultural guidance."
                ),
                "reason": (
                    f"पूर्वानुमान अधिकतम तापमान: {max_temp:.1f}°C ({peak_time} के आसपास) | नियम: > {TEMP_HIGH_THRESHOLD_C:.0f}°C"
                    if lang == "hi"
                    else f"Forecast max temperature: {max_temp:.1f}°C (around {peak_time}) | Rule: > {TEMP_HIGH_THRESHOLD_C:.0f}°C"
                ),
            }
        )

    # Rule 3: Forecast wind speed > 20 km/h
    if max_wind is None:
        advisories.append(
            {
                "rule_id": "wind_data_missing",
                "severity": "info",
                "title": "हवा गति डेटा अपर्याप्त" if lang == "hi" else "Insufficient forecast data",
                "message": (
                    "हवा की गति का पूर्वानुमान डेटा उपलब्ध नहीं है, इसलिए तेज हवा नियम लागू नहीं किया गया।"
                    if lang == "hi"
                    else "Insufficient forecast data: forecast wind speed was not provided."
                ),
                "reason": "Missing field: wind speed" if lang == "en" else "अनुपलब्ध डेटा: हवा की गति",
            }
        )
    elif max_wind > WIND_HIGH_THRESHOLD_KMH:
        peak_time = max_wind_item.get("local_time_str", "")
        advisories.append(
            {
                "rule_id": "strong_wind",
                "severity": "warning",
                "title": "तेज हवा की संभावना" if lang == "hi" else "Strong Wind Caution",
                "message": (
                    "हवा तेज हो सकती है। छिड़काव या पौधों से जुड़े काम से पहले हवा की स्थिति जांचें।"
                    if lang == "hi"
                    else "Strong winds may occur. Check wind conditions before spraying or carrying out delicate plant and field work."
                ),
                "reason": (
                    f"पूर्वानुमान हवा की गति: {max_wind:.1f} km/h (अधिकतम {peak_time} के आसपास) | नियम: > {WIND_HIGH_THRESHOLD_KMH:.0f} km/h"
                    if lang == "hi"
                    else f"Forecast wind speed: {max_wind:.1f} km/h (peak around {peak_time}) | Rule: > {WIND_HIGH_THRESHOLD_KMH:.0f} km/h"
                ),
            }
        )

    # Rule 4: Rain probability is low (< 30%) and wind is not strong (<= 20 km/h)
    if (
        max_rain is not None
        and max_wind is not None
        and max_rain < RAIN_PROB_LOW_THRESHOLD
        and max_wind <= WIND_HIGH_THRESHOLD_KMH
    ):
        advisories.append(
            {
                "rule_id": "low_rain_calm_wind",
                "severity": "success",
                "title": "कम बारिश व सामान्य हवा" if lang == "hi" else "Low Rain & Manageable Wind",
                "message": (
                    "मौसम के उपलब्ध पूर्वानुमान में बारिश की संभावना कम है। खेत का काम करने से पहले ताजा अपडेट देखें।"
                    if lang == "hi"
                    else "Available forecast shows low rain probability and manageable wind speeds. Check the latest updates before field activities."
                ),
                "reason": (
                    f"अधिकतम बारिश संभावना: {max_rain:.0f}% (< {RAIN_PROB_LOW_THRESHOLD:.0f}%) और अधिकतम हवा गति: {max_wind:.1f} km/h (<= {WIND_HIGH_THRESHOLD_KMH:.0f} km/h)"
                    if lang == "hi"
                    else f"Max rain probability: {max_rain:.0f}% (< {RAIN_PROB_LOW_THRESHOLD:.0f}%) and max wind speed: {max_wind:.1f} km/h (<= {WIND_HIGH_THRESHOLD_KMH:.0f} km/h)"
                ),
            }
        )
    elif (
        max_rain is not None
        and max_wind is not None
        and RAIN_PROB_LOW_THRESHOLD <= max_rain < RAIN_PROB_HIGH_THRESHOLD
        and max_wind <= WIND_HIGH_THRESHOLD_KMH
        and (max_temp is None or max_temp <= TEMP_HIGH_THRESHOLD_C)
    ):
        # Intermediate transparent status when rain probability is 30%..69% and no high alert triggered
        advisories.append(
            {
                "rule_id": "moderate_rain_watch",
                "severity": "info",
                "title": "मध्यम बारिश की संभावना" if lang == "hi" else "Moderate Rain Possibility",
                "message": (
                    "पूर्वानुमान में हल्की से मध्यम बारिश की संभावना है। छिड़काव या कटाई से पहले ताजा स्थानीय मौसम अपडेट जांचें।"
                    if lang == "hi"
                    else "Forecast indicates a moderate possibility of rain. Check updated local weather before scheduling spraying or harvesting."
                ),
                "reason": (
                    f"अधिकतम बारिश संभावना: {max_rain:.0f}% (30%–69% के बीच) और अधिकतम हवा गति: {max_wind:.1f} km/h"
                    if lang == "hi"
                    else f"Max rain probability: {max_rain:.0f}% (30%–69% range) and max wind speed: {max_wind:.1f} km/h"
                ),
            }
        )

    return {
        "advisories": advisories,
        "summary": {
            "interval_count": len(scoped),
            "max_rain_prob_pct": max_rain,
            "max_temp_c": max_temp,
            "max_wind_kmh": max_wind,
        },
    }

