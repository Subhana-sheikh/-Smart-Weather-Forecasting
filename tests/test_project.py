"""Unit tests for Weather & Agriculture Advisory services, rules, translations, and charts."""

from __future__ import annotations

import os
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")

from services.air_quality import (
    fetch_air_quality_openmeteo,
    fetch_air_quality_openweather,
)
from services.geocoding import (
    format_location_label,
    search_locations_openmeteo,
    search_locations_openweather,
)
from services.weather_api import (
    fetch_current_weather_openweather,
    fetch_forecast_openweather,
    fetch_weather_bundle_openmeteo,
    summarize_daily_forecast,
)
from utils.advisory import generate_agriculture_advisories
from utils.charts import build_temperature_trend_figure
from utils.translations import (
    get_openweather_aqi_meta,
    translate_condition,
    translate_error,
)

IST = ZoneInfo("Asia/Kolkata")


def _make_interval(
    hours_ahead: int,
    temp_c: float | None = 28.0,
    temp_max_c: float | None = 30.0,
    rain_prob_pct: float | None = 10.0,
    wind_speed_kmh: float | None = 10.0,
) -> dict:
    dt = datetime(2026, 11, 12, 12, 0, tzinfo=IST) + timedelta(hours=hours_ahead)
    return {
        "dt_unix": int(dt.timestamp()),
        "local_dt": dt,
        "local_date": dt.date(),
        "local_time_str": dt.strftime("%d %b, %I:%M %p"),
        "temp_c": temp_c,
        "temp_min_c": temp_c,
        "temp_max_c": temp_max_c,
        "humidity_pct": 50.0,
        "wind_speed_kmh": wind_speed_kmh,
        "rain_prob_pct": rain_prob_pct,
        "weather_main": "Clear",
        "weather_desc": "clear sky",
        "weather_icon_code": "01d",
        "weather_emoji": "☀️",
    }


class TestAgricultureAdvisory(unittest.TestCase):
    def test_high_rain_rule_triggers_with_exact_value(self) -> None:
        intervals = [_make_interval(3, rain_prob_pct=82.0, wind_speed_kmh=12.0)]
        res = generate_agriculture_advisories(intervals, lang="hi")
        rule_ids = [a["rule_id"] for a in res["advisories"]]
        self.assertIn("high_rain_probability", rule_ids)
        rain_adv = next(a for a in res["advisories"] if a["rule_id"] == "high_rain_probability")
        self.assertIn("82%", rain_adv["reason"])
        self.assertIn("बारिश की संभावना अधिक है", rain_adv["message"])

    def test_high_temp_and_strong_wind_rules(self) -> None:
        intervals = [
            _make_interval(6, temp_c=41.5, temp_max_c=42.3, rain_prob_pct=15.0, wind_speed_kmh=26.4)
        ]
        res = generate_agriculture_advisories(intervals, lang="en")
        rule_ids = {a["rule_id"] for a in res["advisories"]}
        self.assertIn("high_temperature", rule_ids)
        self.assertIn("strong_wind", rule_ids)
        self.assertNotIn("low_rain_calm_wind", rule_ids)

    def test_low_rain_and_calm_wind_rule(self) -> None:
        intervals = [_make_interval(3, temp_c=29.0, temp_max_c=31.0, rain_prob_pct=10.0, wind_speed_kmh=14.0)]
        res = generate_agriculture_advisories(intervals, lang="hi")
        rule_ids = [a["rule_id"] for a in res["advisories"]]
        self.assertEqual(rule_ids, ["low_rain_calm_wind"])
        self.assertIn("बारिश की संभावना कम है", res["advisories"][0]["message"])

    def test_missing_fields_emit_insufficient_data_without_triggering(self) -> None:
        intervals = [_make_interval(3, temp_c=None, temp_max_c=None, rain_prob_pct=None, wind_speed_kmh=None)]
        res = generate_agriculture_advisories(intervals, lang="en")
        messages = " ".join(a["message"] for a in res["advisories"])
        self.assertIn("Insufficient forecast data", messages)
        rule_ids = {a["rule_id"] for a in res["advisories"]}
        self.assertEqual(rule_ids, {"rain_data_missing", "temp_data_missing", "wind_data_missing"})

    def test_empty_intervals_emit_insufficient_data(self) -> None:
        res = generate_agriculture_advisories([], lang="en")
        self.assertEqual(res["advisories"][0]["rule_id"], "insufficient_forecast_data")


class TestOpenWeatherServices(unittest.TestCase):
    @patch("services.http_client.requests.get")
    def test_geocoding_disambiguation_and_india_filter(self, mock_get: Mock) -> None:
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = [
            {"name": "Bilaspur", "state": "Chhattisgarh", "country": "IN", "lat": 22.08, "lon": 82.15},
            {"name": "Bilaspur", "state": "Himachal Pradesh", "country": "IN", "lat": 31.33, "lon": 76.76},
            {"name": "Bilaspur", "state": "SomeForeign", "country": "PK", "lat": 30.0, "lon": 70.0},
        ]
        mock_get.return_value = mock_resp

        res = search_locations_openweather("Bilaspur", api_key="valid_test_key_123", india_only=True)
        self.assertTrue(res["ok"])
        self.assertEqual(len(res["results"]), 2)
        labels = [format_location_label(loc) for loc in res["results"]]
        self.assertIn("Bilaspur, Chhattisgarh, IN", labels)
        self.assertIn("Bilaspur, Himachal Pradesh, IN", labels)

    @patch("services.http_client.requests.get")
    def test_invalid_api_key_handling_never_leaks_key(self, mock_get: Mock) -> None:
        mock_resp = Mock(status_code=401)
        mock_resp.json.return_value = {"cod": 401, "message": "Invalid API key"}
        mock_get.return_value = mock_resp

        secret = "SUPER_SECRET_OPENWEATHER_KEY_999"
        res = fetch_current_weather_openweather(23.2599, 77.4126, api_key=secret)
        self.assertFalse(res["ok"])
        self.assertEqual(res["error_code"], "invalid_api_key")
        self.assertNotIn(secret, res["error_detail"])

    @patch("services.http_client.requests.get")
    def test_current_weather_converts_ms_to_kmh(self, mock_get: Mock) -> None:
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = {
            "name": "Bhopal",
            "dt": 1762930000,
            "timezone": 19800,
            "main": {"temp": 29.4, "feels_like": 28.9, "humidity": 42, "pressure": 1014},
            "wind": {"speed": 5.0},
            "clouds": {"all": 10},
            "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
            "sys": {"sunrise": 1762909000, "sunset": 1762949000},
        }
        mock_get.return_value = mock_resp

        res = fetch_current_weather_openweather(23.2599, 77.4126, api_key="valid_test_key_123")
        self.assertTrue(res["ok"])
        self.assertEqual(res["data"]["wind_speed_kmh"], 18.0)
        self.assertEqual(res["data"]["temp_c"], 29.4)

    @patch("services.http_client.requests.get")
    def test_forecast_converts_pop_and_builds_daily_summary_and_chart(self, mock_get: Mock) -> None:
        mock_resp = Mock(status_code=200)
        base_ts = 1762920000
        mock_resp.json.return_value = {
            "city": {"name": "Bhopal", "timezone": 19800},
            "list": [
                {
                    "dt": base_ts + i * 10800,
                    "main": {"temp": 22.0 + (i % 4) * 3, "temp_min": 21.0, "temp_max": 31.0},
                    "wind": {"speed": 4.0},
                    "pop": 0.75 if i == 2 else 0.1,
                    "weather": [{"main": "Rain", "description": "light rain", "icon": "10d"}],
                }
                for i in range(16)
            ],
        }
        mock_get.return_value = mock_resp

        res = fetch_forecast_openweather(23.2599, 77.4126, api_key="valid_test_key_123")
        self.assertTrue(res["ok"])
        self.assertEqual(res["intervals"][2]["rain_prob_pct"], 75.0)
        self.assertEqual(res["intervals"][0]["wind_speed_kmh"], 14.4)
        self.assertFalse(res["daily_df"].empty)

        fig = build_temperature_trend_figure(res["daily_df"], "Bhopal, Madhya Pradesh, IN")
        self.assertIsNotNone(fig)

    @patch("services.http_client.requests.get")
    def test_air_quality_parsing(self, mock_get: Mock) -> None:
        mock_resp = Mock(status_code=200)
        mock_resp.json.return_value = {
            "list": [
                {
                    "dt": 1762930000,
                    "main": {"aqi": 3},
                    "components": {
                        "pm2_5": 35.4,
                        "pm10": 62.1,
                        "no2": 18.2,
                        "o3": 45.0,
                        "so2": 6.1,
                        "co": 410.5,
                    },
                }
            ]
        }
        mock_get.return_value = mock_resp

        res = fetch_air_quality_openweather(23.2599, 77.4126, api_key="valid_test_key_123", tz_offset_sec=19800)
        self.assertTrue(res["ok"])
        self.assertEqual(res["scale_type"], "openweather_1_to_5")
        self.assertEqual(res["data"]["aqi"], 3)
        self.assertEqual(res["data"]["pm2_5"], 35.4)


class TestTranslations(unittest.TestCase):
    def test_weather_condition_translation_and_unmapped_fallback(self) -> None:
        self.assertEqual(translate_condition("clear sky", "hi"), "साफ आसमान")
        unmapped = translate_condition("volcanic ash", "hi")
        self.assertIn("volcanic ash", unmapped)

    def test_aqi_and_error_translation(self) -> None:
        meta = get_openweather_aqi_meta(1, "hi")
        self.assertEqual(meta["label"], "अच्छा")
        err = translate_error("location_not_found", None, "hi")
        self.assertIn("स्थान नहीं मिला", err)


class TestSummarizeEmpty(unittest.TestCase):
    def test_summarize_empty_returns_empty_dataframe(self) -> None:
        df = summarize_daily_forecast([])
        self.assertTrue(df.empty)


class TestOpenMeteoFallback(unittest.TestCase):
    @patch("services.http_client.requests.get")
    def test_openmeteo_geocoding_weather_and_aqi(self, mock_get: Mock) -> None:
        def fake_get(url, params=None, timeout=12):
            resp = Mock(status_code=200)
            if "geocoding-api.open-meteo.com" in url:
                resp.json.return_value = {
                    "results": [
                        {
                            "name": "Bhopal",
                            "admin1": "Madhya Pradesh",
                            "country_code": "IN",
                            "latitude": 23.2599,
                            "longitude": 77.4126,
                        }
                    ]
                }
            elif "air-quality-api.open-meteo.com" in url:
                resp.json.return_value = {
                    "current": {
                        "time": "2026-11-12T11:00",
                        "european_aqi": 42,
                        "pm2_5": 24.5,
                        "pm10": 48.0,
                        "nitrogen_dioxide": 14.1,
                        "ozone": 52.3,
                        "sulphur_dioxide": 5.2,
                        "carbon_monoxide": 310.0,
                    }
                }
            else:
                resp.json.return_value = {
                    "utc_offset_seconds": 19800,
                    "current": {
                        "time": "2026-11-12T11:00",
                        "temperature_2m": 28.4,
                        "relative_humidity_2m": 45,
                        "apparent_temperature": 27.9,
                        "pressure_msl": 1014,
                        "cloud_cover": 15,
                        "wind_speed_10m": 11.2,
                        "weather_code": 1,
                        "is_day": 1,
                    },
                    "hourly": {
                        "time": ["2026-11-12T12:00", "2026-11-12T15:00"],
                        "temperature_2m": [29.1, 30.2],
                        "precipitation_probability": [5, 10],
                        "wind_speed_10m": [11.5, 12.0],
                        "weather_code": [1, 2],
                    },
                    "daily": {
                        "time": ["2026-11-12", "2026-11-13"],
                        "weather_code": [1, 2],
                        "temperature_2m_max": [30.2, 31.0],
                        "temperature_2m_min": [16.5, 17.0],
                        "precipitation_probability_max": [10, 15],
                        "wind_speed_10m_max": [14.0, 15.2],
                        "sunrise": ["2026-11-12T06:30", "2026-11-13T06:31"],
                        "sunset": ["2026-11-12T17:38", "2026-11-13T17:38"],
                    },
                }
            return resp

        mock_get.side_effect = fake_get
        geo = search_locations_openmeteo("Bhopal")
        self.assertTrue(geo["ok"])
        bundle = fetch_weather_bundle_openmeteo(23.2599, 77.4126)
        self.assertTrue(bundle["current"]["ok"])
        self.assertTrue(bundle["forecast"]["ok"])
        self.assertEqual(bundle["current"]["data"]["temp_c"], 28.4)
        aqi = fetch_air_quality_openmeteo(23.2599, 77.4126)
        self.assertTrue(aqi["ok"])
        self.assertEqual(aqi["scale_type"], "openmeteo_european_aqi")


class TestStreamlitAppSmoke(unittest.TestCase):
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": ""}, clear=False)
    def test_app_renders_missing_key_banner_and_hindi_toggle(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=60)
        at.run()
        self.assertFalse(at.exception)
        self.assertTrue(any("OpenWeather API key" in w.value for w in at.warning))

        # Switch language to Hindi
        at.radio[0].set_value("hi").run()
        self.assertFalse(at.exception)
        self.assertTrue(any("OpenWeather API कुंजी" in w.value for w in at.warning))

    @patch("services.http_client.requests.get")
    @patch.dict(os.environ, {"OPENWEATHER_API_KEY": "valid_demo_key_12345"}, clear=False)
    def test_app_renders_full_openweather_dashboard(self, mock_get: Mock) -> None:
        from streamlit.testing.v1 import AppTest

        base_ts = 1762920000

        def fake_get(url, params=None, timeout=12):
            resp = Mock(status_code=200)
            if "/geo/1.0/direct" in url:
                resp.json.return_value = [
                    {
                        "name": "Bhopal",
                        "state": "Madhya Pradesh",
                        "country": "IN",
                        "lat": 23.2599,
                        "lon": 77.4126,
                    }
                ]
            elif "/data/2.5/weather" in url:
                resp.json.return_value = {
                    "name": "Bhopal",
                    "dt": base_ts,
                    "timezone": 19800,
                    "main": {"temp": 29.0, "feels_like": 28.5, "humidity": 44, "pressure": 1013},
                    "wind": {"speed": 3.5},
                    "clouds": {"all": 10},
                    "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
                    "sys": {"sunrise": base_ts - 18000, "sunset": base_ts + 22000},
                }
            elif "/data/2.5/forecast" in url:
                resp.json.return_value = {
                    "city": {"name": "Bhopal", "timezone": 19800},
                    "list": [
                        {
                            "dt": base_ts + i * 10800,
                            "main": {"temp": 25.0 + (i % 4) * 2, "temp_min": 21.0, "temp_max": 32.0},
                            "wind": {"speed": 3.0},
                            "pop": 0.15,
                            "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
                        }
                        for i in range(16)
                    ],
                }
            elif "/data/2.5/air_pollution" in url:
                resp.json.return_value = {
                    "list": [
                        {
                            "dt": base_ts,
                            "main": {"aqi": 2},
                            "components": {
                                "pm2_5": 18.0,
                                "pm10": 32.0,
                                "no2": 10.0,
                                "o3": 40.0,
                                "so2": 4.0,
                                "co": 250.0,
                            },
                        }
                    ]
                }
            return resp

        mock_get.side_effect = fake_get
        at = AppTest.from_file(APP_PATH, default_timeout=60)
        at.run()
        self.assertFalse(at.exception)
        rendered_html = " ".join(m.value for m in at.markdown)
        self.assertIn("Bhopal, Madhya Pradesh, IN", rendered_html)
        self.assertIn("29.0°C", rendered_html)
        self.assertIn("OpenWeather AQI", rendered_html)


if __name__ == "__main__":
    unittest.main()

