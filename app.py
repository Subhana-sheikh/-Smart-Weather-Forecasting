"""Main Streamlit application for MP Smart Weather & Agriculture Advisory System."""

from __future__ import annotations

import html
import time
from typing import Any, Callable

import pandas as pd
import streamlit as st

from services.air_quality import (
    fetch_air_quality_openmeteo,
    fetch_air_quality_openweather,
)
from services.geocoding import (
    format_location_label,
    search_locations_openmeteo,
    search_locations_openweather,
)
from services.http_client import resolve_openweather_api_key
from services.weather_api import (
    fetch_current_weather_openweather,
    fetch_forecast_openweather,
    fetch_weather_bundle_openmeteo,
)
from utils.advisory import generate_agriculture_advisories
from utils.charts import build_temperature_trend_figure
from utils.translations import (
    get_european_aqi_meta,
    get_openweather_aqi_meta,
    t,
    translate_condition,
    translate_error,
    translate_weekday,
)

CACHE_TTL_SECONDS = 600
QUICK_DEMO_CITIES = [
    "Bhopal",
    "Indore",
    "Jabalpur",
    "Gwalior",
    "Ujjain",
    "Sagar",
    "Rewa",
    "Jaipur",
    "Nagpur",
]


st.set_page_config(
    page_title="MP Smart Weather & Agriculture Advisory",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def _get_success_cache() -> dict[tuple[Any, ...], tuple[float, Any]]:
    """In-memory TTL cache storing only successful API responses."""
    return {}


def _cached_success_call(
    cache_key: tuple[Any, ...],
    fn: Callable[[], dict[str, Any]],
    success_check: Callable[[dict[str, Any]], bool] | None = None,
    ttl: int = CACHE_TTL_SECONDS,
) -> dict[str, Any]:
    """Return cached successful result within TTL, otherwise invoke fn() live."""
    store = _get_success_cache()
    now = time.time()
    cached = store.get(cache_key)
    if cached is not None:
        ts, value = cached
        if now - ts < ttl:
            return value
        store.pop(cache_key, None)

    result = fn()
    is_ok = success_check(result) if success_check else bool(result.get("ok"))
    if is_ok:
        store[cache_key] = (now, result)
    return result


def _inject_styles() -> None:
    """Apply deep-navy / sky-blue dashboard theme with crisp light cards."""
    st.markdown(
        """
<style>
.stApp {
    background: linear-gradient(180deg, #071426 0%, #0C1F3B 55%, #0F294D 100%);
    color: #F1F5F9;
}
[data-testid="stSidebar"] {
    background-color: #09182E;
    border-right: 1px solid rgba(56, 189, 248, 0.18);
}
.hero-header {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.20), rgba(56, 189, 248, 0.08));
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 1.85rem;
    font-weight: 800;
    color: #F8FAFC;
    margin: 0 0 0.25rem 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 0.98rem;
    color: #BAE6FD;
    margin: 0;
}
.light-card {
    background: #F8FAFC;
    color: #0F172A;
    border-radius: 16px;
    padding: 1.2rem 1.35rem;
    box-shadow: 0 10px 25px rgba(2, 12, 27, 0.28);
    border: 1px solid #E2E8F0;
    margin-bottom: 0.9rem;
}
.weather-hero-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 100%);
    color: #0F172A;
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 12px 28px rgba(2, 12, 27, 0.32);
    border: 1px solid #BAE6FD;
    margin-bottom: 1rem;
}
.metric-card {
    background: #F8FAFC;
    color: #0F172A;
    border-radius: 14px;
    padding: 0.95rem 1.05rem;
    box-shadow: 0 6px 18px rgba(2, 12, 27, 0.22);
    border: 1px solid #E2E8F0;
    border-top: 3px solid #38BDF8;
    margin-bottom: 0.75rem;
}
.metric-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-bottom: 0.25rem;
}
.metric-value {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.2;
}
.forecast-card {
    background: #F8FAFC;
    color: #0F172A;
    border-radius: 14px;
    padding: 0.95rem 0.85rem;
    box-shadow: 0 6px 16px rgba(2, 12, 27, 0.22);
    border: 1px solid #E2E8F0;
    text-align: center;
    height: 100%;
    margin-bottom: 0.65rem;
}
.forecast-day {
    font-size: 0.98rem;
    font-weight: 800;
    color: #0F172A;
}
.forecast-date {
    font-size: 0.82rem;
    color: #475569;
    margin-bottom: 0.45rem;
}
.forecast-cond {
    font-size: 0.88rem;
    font-weight: 600;
    color: #1E293B;
    min-height: 2.3rem;
    display: flex;
    align-items: center;
    justify-content: center;
}
.forecast-temp {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0369A1;
    margin: 0.35rem 0;
}
.forecast-meta {
    font-size: 0.82rem;
    color: #334155;
    line-height: 1.45;
}
.advisory-card {
    background: #FFFFFF;
    color: #0F172A;
    border-radius: 14px;
    padding: 1.05rem 1.25rem;
    box-shadow: 0 8px 20px rgba(2, 12, 27, 0.24);
    border: 1px solid #E2E8F0;
    margin-bottom: 0.85rem;
}
.advisory-warning { border-left: 6px solid #EA580C; }
.advisory-danger { border-left: 6px solid #DC2626; }
.advisory-success { border-left: 6px solid #16A34A; }
.advisory-info { border-left: 6px solid #0284C7; }
.advisory-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 0.35rem;
}
.advisory-msg {
    font-size: 0.98rem;
    color: #1E293B;
    line-height: 1.5;
    margin-bottom: 0.55rem;
}
.advisory-why {
    background: #F1F5F9;
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    font-size: 0.86rem;
    color: #334155;
}
.location-banner {
    background: rgba(15, 39, 71, 0.92);
    border: 1px solid rgba(56, 189, 248, 0.40);
    border-radius: 12px;
    padding: 0.85rem 1.15rem;
    margin: 0.65rem 0 1rem 0;
    color: #E2E8F0;
}
.provider-badge {
    display: inline-block;
    background: #0284C7;
    color: #FFFFFF;
    padding: 0.18rem 0.6rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
}
.unavailable-card {
    background: #F1F5F9;
    color: #334155;
    border: 1px dashed #94A3B8;
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.8rem;
}
.aqi-pill {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    font-weight: 800;
    font-size: 0.95rem;
}
.section-heading {
    font-size: 1.3rem;
    font-weight: 800;
    color: #F8FAFC;
    margin: 1.1rem 0 0.55rem 0;
    border-left: 4px solid #38BDF8;
    padding-left: 0.65rem;
}
.footer-box {
    background: rgba(9, 24, 46, 0.85);
    border-top: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-top: 1.5rem;
    color: #CBD5E1;
    font-size: 0.88rem;
}
@media (max-width: 768px) {
    .hero-title { font-size: 1.4rem; }
    .weather-hero-card { padding: 1rem; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def _init_session_state() -> None:
    """Initialize required Streamlit session state defaults."""
    defaults: dict[str, Any] = {
        "lang": "en",
        "search_query": "Bhopal",
        "search_input": "Bhopal",
        "india_only": True,
        "provider_mode": "openweather",
        "selected_loc_idx": 0,
        "session_api_key": "",
        "horizon_choice": "5d",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _select_quick_city(city: str) -> None:
    """Callback to update search query and input cleanly when a quick city is clicked."""
    st.session_state["search_query"] = city
    st.session_state["search_input"] = city
    st.session_state["selected_loc_idx"] = 0


def _activate_openmeteo_fallback() -> None:
    """Callback to switch provider mode to Open-Meteo fallback cleanly."""
    st.session_state["provider_mode"] = "openmeteo"
    st.session_state["selected_loc_idx"] = 0


def _reset_loc_index() -> None:
    """Reset location selection index when search scope or provider changes."""
    st.session_state["selected_loc_idx"] = 0


def _fmt_num(val: float | int | None, unit: str, decimals: int = 1, lang: str = "en") -> str:
    """Format numeric metric value with unit, or localized 'Data unavailable'."""
    if val is None or pd.isna(val):
        return t("data_unavailable", lang)
    if decimals == 0:
        return f"{val:.0f}{unit}"
    return f"{val:.{decimals}f}{unit}"


def _render_unavailable_section(
    error_code: str | None,
    error_detail: str | None,
    lang: str,
    retry_key: str,
) -> None:
    """Display a clean themed unavailable/error card with a Retry button."""
    err_text = html.escape(translate_error(error_code, error_detail, lang))
    title = html.escape(t("data_unavailable", lang))
    st.markdown(
        f'<div class="unavailable-card"><strong>⚠️ {title}</strong><br/>{err_text}</div>',
        unsafe_allow_html=True,
    )
    if st.button(f"🔄 {t('retry_button', lang)}", key=retry_key):
        _get_success_cache().clear()
        st.rerun()


def _render_sidebar(lang: str) -> tuple[str | None, str]:
    """Render sidebar configuration, provider toggle, quick locations, and viva help."""
    with st.sidebar:
        st.subheader(t("sidebar_settings", lang))

        provider_options = ["openweather", "openmeteo"]
        st.radio(
            t("sidebar_provider_label", lang),
            options=provider_options,
            key="provider_mode",
            on_change=_reset_loc_index,
            format_func=lambda opt: (
                t("provider_openweather", lang)
                if opt == "openweather"
                else t("provider_openmeteo", lang)
            ),
        )

        st.text_input(
            t("api_key_input_label", lang),
            key="session_api_key",
            type="password",
            help=t("api_key_input_help", lang),
        )

        api_key, resolved_source = resolve_openweather_api_key(st.session_state["session_api_key"])
        if api_key:
            st.success(t("api_key_status_ok", lang, source=resolved_source))
        else:
            st.warning(t("api_key_status_missing", lang))

        st.checkbox(
            t("india_only_label", lang),
            key="india_only",
            on_change=_reset_loc_index,
        )

        if st.button(f"🔄 {t('refresh_btn', lang)}", width="stretch"):
            _get_success_cache().clear()
            st.rerun()

        st.divider()
        st.markdown(f"**{t('quick_cities_header', lang)}**")
        cols = st.columns(2)
        for idx, city in enumerate(QUICK_DEMO_CITIES):
            with cols[idx % 2]:
                label = f"{city} (MP)" if city == "Bhopal" else city
                st.button(
                    label,
                    key=f"quick_{city}",
                    width="stretch",
                    on_click=_select_quick_city,
                    args=(city,),
                )

        st.divider()
        with st.expander(t("viva_expander_title", lang)):
            st.markdown(t("viva_expander_body", lang))

    return api_key, resolved_source


def _render_current_weather(
    current_res: dict[str, Any],
    location_label: str,
    lang: str,
) -> None:
    """Render the current weather hero card and six metric cards."""
    st.markdown(
        f'<div class="section-heading">🌤️ {html.escape(t("current_weather_heading", lang))}</div>',
        unsafe_allow_html=True,
    )
    if not current_res.get("ok"):
        _render_unavailable_section(
            current_res.get("error_code"),
            current_res.get("error_detail"),
            lang,
            retry_key="retry_current",
        )
        return

    data = current_res["data"]
    temp_str = _fmt_num(data.get("temp_c"), "°C", decimals=1, lang=lang)
    feels_str = _fmt_num(data.get("feels_like_c"), "°C", decimals=1, lang=lang)
    cond_str = translate_condition(data.get("weather_desc"), lang)
    obs_str = data.get("observation_time") or t("data_unavailable", lang)
    provider_str = current_res.get("provider", "Unknown")

    icon_url = data.get("weather_icon_url")
    emoji = data.get("weather_emoji") or "🌤️"
    icon_html = (
        f'<img src="{html.escape(icon_url)}" width="74" alt="weather icon" style="vertical-align:middle;" />'
        if icon_url
        else f'<span style="font-size:3rem;">{emoji}</span>'
    )

    st.markdown(
        f"""
<div class="weather-hero-card">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
<div>
<div style="font-size:0.9rem; font-weight:700; color:#0369A1;">📍 {html.escape(location_label)}</div>
<div style="font-size:2.9rem; font-weight:900; color:#0F172A; line-height:1.1; margin:0.25rem 0;">{html.escape(temp_str)}</div>
<div style="font-size:1.1rem; font-weight:700; color:#1E293B;">{html.escape(cond_str)}</div>
</div>
<div style="text-align:right;">
<div>{icon_html}</div>
<div style="font-size:0.92rem; color:#334155;"><strong>{html.escape(t("feels_like", lang))}:</strong> {html.escape(feels_str)}</div>
<div style="font-size:0.84rem; color:#475569;"><strong>{html.escape(t("observation_time", lang))}:</strong> {html.escape(str(obs_str))}</div>
<div style="font-size:0.78rem; color:#0284C7; font-weight:700; margin-top:0.2rem;">{html.escape(provider_str)}</div>
</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    metrics = [
        ("💧", t("humidity", lang), _fmt_num(data.get("humidity_pct"), "%", decimals=0, lang=lang)),
        ("💨", t("wind_speed", lang), _fmt_num(data.get("wind_speed_kmh"), " km/h", decimals=1, lang=lang)),
        ("🧭", t("pressure", lang), _fmt_num(data.get("pressure_hpa"), " hPa", decimals=0, lang=lang)),
        ("☁️", t("cloud_cover", lang), _fmt_num(data.get("clouds_pct"), "%", decimals=0, lang=lang)),
        ("🌅", t("sunrise", lang), data.get("sunrise_time") or t("data_unavailable", lang)),
        ("🌇", t("sunset", lang), data.get("sunset_time") or t("data_unavailable", lang)),
    ]

    row1 = st.columns(3)
    for col, (icon, label, val) in zip(row1, metrics[:3]):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{icon} {html.escape(label)}</div>'
                f'<div class="metric-value">{html.escape(str(val))}</div></div>',
                unsafe_allow_html=True,
            )

    row2 = st.columns(3)
    for col, (icon, label, val) in zip(row2, metrics[3:]):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{icon} {html.escape(label)}</div>'
                f'<div class="metric-value">{html.escape(str(val))}</div></div>',
                unsafe_allow_html=True,
            )


def _render_forecast_section(
    forecast_res: dict[str, Any],
    location_label: str,
    lang: str,
) -> None:
    """Render five-day forecast cards and Matplotlib daily min/max temperature chart."""
    st.markdown(
        f'<div class="section-heading">📅 {html.escape(t("forecast_heading", lang))}</div>',
        unsafe_allow_html=True,
    )
    if not forecast_res.get("ok"):
        _render_unavailable_section(
            forecast_res.get("error_code"),
            forecast_res.get("error_detail"),
            lang,
            retry_key="retry_forecast",
        )
        return

    interval_label = forecast_res.get("interval_label", "3-hour")
    st.caption(t("forecast_caption", lang, interval=interval_label))

    daily_df: pd.DataFrame = forecast_res.get("daily_df")
    if daily_df is None or daily_df.empty:
        _render_unavailable_section("invalid_response", "No daily summary rows available.", lang, "retry_forecast_df")
        return

    cols = st.columns(len(daily_df))
    for col, (_, row) in zip(cols, daily_df.iterrows()):
        day_name = translate_weekday(str(row["weekday_short"]), lang)
        date_str = str(row["date_str"])
        cond_str = translate_condition(row.get("condition_desc"), lang)
        min_t = _fmt_num(row.get("temp_min_c"), "°C", decimals=1, lang=lang)
        max_t = _fmt_num(row.get("temp_max_c"), "°C", decimals=1, lang=lang)
        rain_p = _fmt_num(row.get("max_rain_prob_pct"), "%", decimals=0, lang=lang)
        wind_k = _fmt_num(row.get("max_wind_kmh"), " km/h", decimals=1, lang=lang)
        icon_url = row.get("weather_icon_url")
        emoji = row.get("weather_emoji") or "🌤️"
        icon_html = (
            f'<img src="{html.escape(icon_url)}" width="48" alt="icon" />'
            if icon_url
            else f'<div style="font-size:1.9rem; margin:0.2rem 0;">{emoji}</div>'
        )
        interval_note = (
            f'<div style="font-size:0.74rem; color:#64748B; margin-top:0.25rem;">'
            f'{html.escape(t("intervals_count", lang, n=int(row["interval_count"])))}</div>'
            if pd.notna(row.get("interval_count"))
            else ""
        )

        with col:
            st.markdown(
                f"""
<div class="forecast-card">
<div class="forecast-day">{html.escape(day_name)}</div>
<div class="forecast-date">{html.escape(date_str)}</div>
{icon_html}
<div class="forecast-cond">{html.escape(cond_str)}</div>
<div class="forecast-temp">{html.escape(min_t)} / {html.escape(max_t)}</div>
<div class="forecast-meta">
🌧️ {html.escape(t("rain_prob", lang))}: <strong>{html.escape(rain_p)}</strong><br/>
💨 {html.escape(t("wind_speed", lang))}: <strong>{html.escape(wind_k)}</strong>
</div>
{interval_note}
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown(f"**📈 {t('chart_heading', lang)}**")
    fig = build_temperature_trend_figure(
        daily_df,
        location_label=location_label,
        interval_label=interval_label,
    )
    if fig is not None:
        st.pyplot(fig, width="stretch")
    else:
        st.info(t("data_unavailable", lang))


def _render_advisory_section(forecast_res: dict[str, Any], lang: str) -> None:
    """Render rule-based smart agriculture advisory cards with exact observed triggers."""
    st.markdown(
        f'<div class="section-heading">🌾 {html.escape(t("advisory_heading", lang))}</div>',
        unsafe_allow_html=True,
    )
    if not forecast_res.get("ok"):
        _render_unavailable_section(
            forecast_res.get("error_code"),
            forecast_res.get("error_detail"),
            lang,
            retry_key="retry_advisory",
        )
        return

    horizon_map = {
        "5d": (t("horizon_5d", lang), None),
        "48h": (t("horizon_48h", lang), 48),
        "24h": (t("horizon_24h", lang), 24),
    }
    selected_horizon = st.radio(
        t("advisory_horizon_label", lang),
        options=["5d", "48h", "24h"],
        index=["5d", "48h", "24h"].index(st.session_state["horizon_choice"]),
        horizontal=True,
        format_func=lambda key: horizon_map[key][0],
    )
    st.session_state["horizon_choice"] = selected_horizon
    horizon_label, horizon_hours = horizon_map[selected_horizon]

    advisory_output = generate_agriculture_advisories(
        forecast_res.get("intervals", []),
        horizon_hours=horizon_hours,
        lang=lang,
    )
    summary = advisory_output["summary"]

    # Transparent summary of observed forecast inputs
    s_cols = st.columns(3)
    with s_cols[0]:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">🌧️ {html.escape(t("rain_prob", lang))} (Max)</div>'
            f'<div class="metric-value">{html.escape(_fmt_num(summary.get("max_rain_prob_pct"), "%", 0, lang))}</div></div>',
            unsafe_allow_html=True,
        )
    with s_cols[1]:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">🌡️ {html.escape(t("max_temp", lang))}</div>'
            f'<div class="metric-value">{html.escape(_fmt_num(summary.get("max_temp_c"), "°C", 1, lang))}</div></div>',
            unsafe_allow_html=True,
        )
    with s_cols[2]:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">💨 {html.escape(t("wind_speed", lang))} (Max)</div>'
            f'<div class="metric-value">{html.escape(_fmt_num(summary.get("max_wind_kmh"), " km/h", 1, lang))}</div></div>',
            unsafe_allow_html=True,
        )

    icon_by_severity = {
        "danger": "🔥",
        "warning": "⚠️",
        "success": "✅",
        "info": "ℹ️",
    }
    for adv in advisory_output["advisories"]:
        sev = adv.get("severity", "info")
        if sev not in {"danger", "warning", "success", "info"}:
            sev = "info"
        icon = icon_by_severity[sev]
        st.markdown(
            f"""
<div class="advisory-card advisory-{sev}">
<div class="advisory-title">{icon} {html.escape(adv["title"])}</div>
<div class="advisory-msg">{html.escape(adv["message"])}</div>
<div class="advisory-why"><strong>{html.escape(t("why_this_advice", lang))}:</strong> {html.escape(adv["reason"])} ({html.escape(horizon_label)})</div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.info(t("advisory_disclaimer", lang))


def _render_aqi_section(aqi_res: dict[str, Any], lang: str) -> None:
    """Render Air Quality Index card with clear scale attribution and pollutants."""
    st.markdown(
        f'<div class="section-heading">🌬️ {html.escape(t("aqi_heading", lang))}</div>',
        unsafe_allow_html=True,
    )
    if not aqi_res.get("ok"):
        _render_unavailable_section(
            aqi_res.get("error_code"),
            aqi_res.get("error_detail"),
            lang,
            retry_key="retry_aqi",
        )
        return

    data = aqi_res["data"]
    scale_type = aqi_res.get("scale_type", "openweather_1_to_5")
    aqi_val = data.get("aqi")

    if scale_type == "openweather_1_to_5":
        meta = get_openweather_aqi_meta(aqi_val, lang)
        scale_title = t("aqi_scale_ow", lang)
        scale_note = t("aqi_scale_note_ow", lang)
        aqi_display = f"{aqi_val} / 5" if aqi_val is not None else t("data_unavailable", lang)
    else:
        meta = get_european_aqi_meta(aqi_val, lang)
        scale_title = t("aqi_scale_om", lang)
        scale_note = t("aqi_scale_note_om", lang)
        aqi_display = f"{aqi_val}" if aqi_val is not None else t("data_unavailable", lang)

    obs_time = data.get("observation_time") or t("data_unavailable", lang)
    provider = aqi_res.get("provider", "Unknown")

    st.markdown(
        f"""
<div class="light-card">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem;">
<div>
<div style="font-size:0.86rem; font-weight:700; color:#475569;">{html.escape(scale_title)} · {html.escape(provider)}</div>
<div style="font-size:1.95rem; font-weight:900; color:#0F172A; margin-top:0.2rem;">{html.escape(aqi_display)}</div>
</div>
<div style="text-align:right;">
<span class="aqi-pill" style="background:{meta['bg']}; color:{meta['color']};">{html.escape(meta['label'])}</span>
<div style="font-size:0.82rem; color:#475569; margin-top:0.35rem;">{html.escape(t("observation_time", lang))}: {html.escape(str(obs_time))}</div>
</div>
</div>
<div style="font-size:0.84rem; color:#475569; margin-top:0.65rem; border-top:1px solid #E2E8F0; padding-top:0.55rem;">
{html.escape(scale_note)}
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(f"**{t('pollutants_heading', lang)}**")
    pollutants = [
        ("PM2.5", data.get("pm2_5")),
        ("PM10", data.get("pm10")),
        ("NO₂", data.get("no2")),
        ("O₃", data.get("o3")),
        ("SO₂", data.get("so2")),
        ("CO", data.get("co")),
    ]
    p_row1 = st.columns(3)
    for col, (name, val) in zip(p_row1, pollutants[:3]):
        with col:
            val_str = f"{val:.2f} μg/m³" if val is not None else t("data_unavailable", lang)
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{html.escape(name)}</div>'
                f'<div class="metric-value">{html.escape(val_str)}</div></div>',
                unsafe_allow_html=True,
            )
    p_row2 = st.columns(3)
    for col, (name, val) in zip(p_row2, pollutants[3:]):
        with col:
            val_str = f"{val:.2f} μg/m³" if val is not None else t("data_unavailable", lang)
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{html.escape(name)}</div>'
                f'<div class="metric-value">{html.escape(val_str)}</div></div>',
                unsafe_allow_html=True,
            )


def main() -> None:
    """Run the Streamlit dashboard application."""
    _init_session_state()
    _inject_styles()

    # Top language bar
    top_col1, top_col2 = st.columns([3.5, 1.5])
    with top_col2:
        lang_choice = st.radio(
            t("language_label", st.session_state["lang"]),
            options=["en", "hi"],
            index=0 if st.session_state["lang"] == "en" else 1,
            horizontal=True,
            format_func=lambda code: "English" if code == "en" else "हिंदी",
        )
        if lang_choice != st.session_state["lang"]:
            st.session_state["lang"] = lang_choice
            st.rerun()

    lang = st.session_state["lang"]

    with top_col1:
        st.markdown(
            f"""
<div class="hero-header">
<div class="hero-title">🌦️ {html.escape(t("app_title", lang))}</div>
<div class="hero-subtitle">{html.escape(t("app_subtitle", lang))}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    api_key, _ = _render_sidebar(lang)

    # Search form
    with st.form(key="location_search_form", clear_on_submit=False):
        s_col1, s_col2 = st.columns([4, 1])
        with s_col1:
            typed_query = st.text_input(
                t("search_label", lang),
                key="search_input",
                placeholder=t("search_placeholder", lang),
                label_visibility="collapsed",
            )
        with s_col2:
            submitted = st.form_submit_button(
                f"🔍 {t('search_button', lang)}",
                width="stretch",
                type="primary",
            )

    if submitted:
        cleaned = typed_query.strip()
        if cleaned != st.session_state["search_query"]:
            st.session_state["search_query"] = cleaned
            st.session_state["selected_loc_idx"] = 0
        elif not cleaned:
            st.session_state["search_query"] = ""

    query = st.session_state["search_query"]
    india_only = st.session_state["india_only"]
    provider_mode = st.session_state["provider_mode"]

    # Handle missing OpenWeather key cleanly before hitting OpenWeather endpoints
    if provider_mode == "openweather" and not api_key:
        st.warning(t("missing_key_banner", lang))
        st.button(
            f"🌐 {t('use_fallback_button', lang)}",
            type="primary",
            on_click=_activate_openmeteo_fallback,
        )
        st.markdown(
            f'<div class="footer-box">{html.escape(t("footer_source", lang))} · {html.escape(t("footer_accuracy", lang))}</div>',
            unsafe_allow_html=True,
        )
        return

    # 1. Geocoding lookup
    if provider_mode == "openweather":
        geo_res = _cached_success_call(
            ("geo_ow", query.lower(), india_only),
            lambda: search_locations_openweather(query, api_key=api_key, india_only=india_only),
        )
    else:
        geo_res = _cached_success_call(
            ("geo_om", query.lower(), india_only),
            lambda: search_locations_openmeteo(query, india_only=india_only),
        )

    if not geo_res.get("ok"):
        st.error(translate_error(geo_res.get("error_code"), geo_res.get("error_detail"), lang))
        col_r1, col_r2 = st.columns([1, 2])
        with col_r1:
            if st.button(f"🔄 {t('retry_button', lang)}", key="retry_geo"):
                _get_success_cache().clear()
                st.rerun()
        if provider_mode == "openweather":
            with col_r2:
                st.button(
                    f"🌐 {t('use_fallback_button', lang)}",
                    key="fallback_after_geo_err",
                    on_click=_activate_openmeteo_fallback,
                )
        return

    locations = geo_res["results"]
    if st.session_state["selected_loc_idx"] >= len(locations):
        st.session_state["selected_loc_idx"] = 0

    if len(locations) > 1:
        options = list(range(len(locations)))
        chosen_idx = st.selectbox(
            t("choose_location_label", lang),
            options=options,
            index=st.session_state["selected_loc_idx"],
            format_func=lambda idx: (
                f"{format_location_label(locations[idx])} "
                f"({locations[idx]['lat']:.2f}, {locations[idx]['lon']:.2f})"
            ),
        )
        st.session_state["selected_loc_idx"] = chosen_idx

    selected_loc = locations[st.session_state["selected_loc_idx"]]
    loc_label = format_location_label(selected_loc)
    lat = selected_loc["lat"]
    lon = selected_loc["lon"]

    # 2. Fetch current weather, 5-day forecast, and air quality independently
    if provider_mode == "openweather":
        current_res = _cached_success_call(
            ("curr_ow", round(lat, 4), round(lon, 4)),
            lambda: fetch_current_weather_openweather(lat, lon, api_key=api_key),
        )
        forecast_res = _cached_success_call(
            ("fc_ow", round(lat, 4), round(lon, 4)),
            lambda: fetch_forecast_openweather(lat, lon, api_key=api_key),
        )
        tz_offset = (
            current_res["data"].get("timezone_offset_sec")
            if current_res.get("ok")
            else None
        )
        aqi_res = _cached_success_call(
            ("aqi_ow", round(lat, 4), round(lon, 4)),
            lambda: fetch_air_quality_openweather(lat, lon, api_key=api_key, tz_offset_sec=tz_offset),
        )
    else:
        om_bundle = _cached_success_call(
            ("bundle_om", round(lat, 4), round(lon, 4)),
            lambda: fetch_weather_bundle_openmeteo(lat, lon),
            success_check=lambda b: bool(b.get("current", {}).get("ok") or b.get("forecast", {}).get("ok")),
        )
        current_res = om_bundle["current"]
        forecast_res = om_bundle["forecast"]
        aqi_res = _cached_success_call(
            ("aqi_om", round(lat, 4), round(lon, 4)),
            lambda: fetch_air_quality_openmeteo(lat, lon),
        )

    # Determine latest successful update time across endpoints
    fetched_times = [
        r.get("fetched_at")
        for r in (current_res, forecast_res, aqi_res, geo_res)
        if r.get("ok") and r.get("fetched_at")
    ]
    latest_update = fetched_times[0] if fetched_times else t("data_unavailable", lang)
    active_provider = (
        "OpenWeatherMap" if provider_mode == "openweather" else "Open-Meteo (Fallback)"
    )

    st.markdown(
        f"""
<div class="location-banner">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
<div>
<strong style="font-size:1.05rem;">📍 {html.escape(loc_label)}</strong>
<span style="margin-left:0.65rem; font-size:0.86rem; color:#BAE6FD;">
{html.escape(t("location_banner_coords", lang))}: {lat:.3f}, {lon:.3f}
</span>
</div>
<div style="font-size:0.86rem;">
<span class="provider-badge">{html.escape(active_provider)}</span>
<span style="margin-left:0.65rem;">🕒 {html.escape(t("location_banner_updated", lang))}: {html.escape(str(latest_update))}</span>
</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Render main dashboard sections
    _render_current_weather(current_res, loc_label, lang)
    _render_forecast_section(forecast_res, loc_label, lang)
    _render_advisory_section(forecast_res, lang)
    _render_aqi_section(aqi_res, lang)

    # Footer
    st.markdown(
        f"""
<div class="footer-box">
<strong>{html.escape(t("location_banner_provider", lang))}:</strong> {html.escape(active_provider)} ·
<strong>{html.escape(t("location_banner_updated", lang))}:</strong> {html.escape(str(latest_update))}<br/>
{html.escape(t("footer_source", lang))}<br/>
<em>{html.escape(t("footer_accuracy", lang))}</em>
</div>
""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
