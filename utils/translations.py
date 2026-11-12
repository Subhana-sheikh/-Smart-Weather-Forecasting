"""Bilingual (English / Hindi) UI translations and weather condition mappings."""

from __future__ import annotations

from typing import Any

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "MP Smart Weather & Agriculture Advisory",
        "app_subtitle": "Live Weather, 5-Day Forecast, Air Quality & Simple Farmer Guidance across Madhya Pradesh and India",
        "language_label": "Language / भाषा",
        "sidebar_settings": "Settings & Data Source",
        "sidebar_provider_label": "Weather Data Provider",
        "provider_openweather": "OpenWeatherMap (Primary)",
        "provider_openmeteo": "Open-Meteo (Fallback - No Key Needed)",
        "api_key_status_ok": "OpenWeather API key loaded from {source}.",
        "api_key_status_missing": "OpenWeather API key not found in .env or secrets.",
        "api_key_input_label": "Session OpenWeather API Key (optional)",
        "api_key_input_help": "Temporary key for this browser session only. Save it in .env for permanent use.",
        "india_only_label": "Restrict search to India (IN)",
        "quick_cities_header": "Quick Demo Locations (MP & India)",
        "refresh_btn": "Refresh Live Data",
        "viva_expander_title": "How Advisory Rules & Sources Work",
        "viva_expander_body": (
            "- **Live APIs Only:** Every weather, forecast, and AQI metric comes directly from a live API response. "
            "No random or hard-coded values are ever shown.\n"
            "- **Transparent Rules:** Advisories check forecast rain probability (`>= 70%`, `< 30%`), "
            "max temperature (`> 40°C`), and wind speed (`> 20 km/h`).\n"
            "- **Units:** Wind speed in m/s is converted to km/h (`m/s × 3.6`), and `pop` (`0–1`) is converted to `%` (`pop × 100`)."
        ),
        "search_placeholder": "Enter city or district in MP or India (e.g., Bhopal, Indore, Sagar, Jaipur)",
        "search_button": "Search Weather",
        "search_label": "Search City or District",
        "choose_location_label": "Multiple matching locations found. Please select the exact one:",
        "location_banner_coords": "Coordinates",
        "location_banner_provider": "Data Source",
        "location_banner_updated": "Last Updated",
        "current_weather_heading": "Current Weather",
        "feels_like": "Feels Like",
        "observation_time": "Observation Time",
        "humidity": "Humidity",
        "wind_speed": "Wind Speed",
        "pressure": "Pressure",
        "cloud_cover": "Cloud Cover",
        "sunrise": "Sunrise",
        "sunset": "Sunset",
        "forecast_heading": "Five-Day Weather Forecast",
        "forecast_caption": "Daily min/max temperatures, peak rain probability, and peak wind speed derived from {interval} forecast timestamps.",
        "chart_heading": "5-Day Temperature Trend",
        "min_temp": "Min",
        "max_temp": "Max",
        "rain_prob": "Rain Prob.",
        "advisory_heading": "Smart Agriculture Advisory",
        "advisory_horizon_label": "Evaluate forecast rules over:",
        "horizon_5d": "Full 5-Day Forecast",
        "horizon_48h": "Next 48 Hours",
        "horizon_24h": "Next 24 Hours",
        "why_this_advice": "Why this advice?",
        "advisory_inputs_label": "Observed Forecast Extremes ({horizon})",
        "advisory_disclaimer": (
            "Agriculture Safety Note: These rule-based suggestions are general educational guidance only—not "
            "official IMD warnings or crop-specific advice. Consult your local Krishi Vigyan Kendra (KVK), "
            "State Agriculture Department, or agricultural expert before spraying or irrigating."
        ),
        "aqi_heading": "Air Quality Index (AQI)",
        "aqi_scale_ow": "OpenWeather AQI (1–5 Scale)",
        "aqi_scale_om": "Open-Meteo European AQI",
        "aqi_scale_note_ow": "Note: OpenWeather uses a 1 to 5 scale (1 = Good, 5 = Very Poor), which is different from India's CPCB AQI (0–500).",
        "aqi_scale_note_om": "Note: Open-Meteo reports the European AQI index (0–100+), which is different from both OpenWeather (1–5) and India's CPCB AQI (0–500).",
        "pollutants_heading": "Pollutant Concentrations (μg/m³)",
        "data_unavailable": "Data unavailable",
        "retry_button": "Retry Request",
        "use_fallback_button": "Try Open-Meteo Live Fallback",
        "missing_key_banner": (
            "OpenWeather API key is not configured yet. Add `OPENWEATHER_API_KEY` to your `.env` file "
            "(or enter a session key in the sidebar), or click below to view live weather via Open-Meteo fallback."
        ),
        "footer_source": "Primary API: OpenWeatherMap | Optional Fallback: Open-Meteo",
        "footer_accuracy": "Forecasts are estimates and can change; verify official IMD advisories for critical decisions.",
        "original_desc_note": "Provider description",
        "intervals_count": "{n} intervals",
        "err_empty_query": "Please enter a city or district name to search.",
        "err_missing_api_key": "OpenWeather API key is missing. Configure .env or use the Open-Meteo fallback.",
        "err_invalid_api_key": "OpenWeather rejected the API key (HTTP 401). Please check your key or wait if it was just created.",
        "err_rate_limit": "API rate limit reached (HTTP 429). Please wait a moment and retry.",
        "err_location_not_found": "No matching location was found. Check the spelling or try adding the state name (e.g., 'Sagar, MP').",
        "err_timeout": "The weather service timed out. Please try again.",
        "err_network_error": "Network error: unable to reach the weather API. Check your internet connection.",
        "err_api_error": "The weather service returned an error.",
        "err_invalid_response": "Received unexpected or incomplete data from the weather provider.",
    },
    "hi": {
        "app_title": "स्मार्ट मौसम और कृषि सलाह प्रणाली (MP व भारत)",
        "app_subtitle": "मध्य प्रदेश और भारत के शहरों/जिलों के लिए लाइव मौसम, 5-दिन का पूर्वानुमान, वायु गुणवत्ता (AQI) और सरल कृषि मार्गदर्शन",
        "language_label": "Language / भाषा",
        "sidebar_settings": "सेटिंग्स और डेटा स्रोत",
        "sidebar_provider_label": "मौसम डेटा प्रदाता",
        "provider_openweather": "OpenWeatherMap (मुख्य स्रोत)",
        "provider_openmeteo": "Open-Meteo (वैकल्पिक स्रोत - बिना API Key)",
        "api_key_status_ok": "OpenWeather API कुंजी {source} से लोड हो गई है।",
        "api_key_status_missing": ".env या secrets में OpenWeather API कुंजी नहीं मिली।",
        "api_key_input_label": "सेशन OpenWeather API Key (वैकल्पिक)",
        "api_key_input_help": "केवल इस सेशन के लिए। स्थायी उपयोग के लिए इसे .env फ़ाइल में सेव करें।",
        "india_only_label": "खोज को केवल भारत (IN) तक सीमित रखें",
        "quick_cities_header": "त्वरित शहर चुनें (MP व भारत)",
        "refresh_btn": "ताजा लाइव डेटा लाएं",
        "viva_expander_title": "कृषि सलाह नियम और डेटा स्रोत की जानकारी",
        "viva_expander_body": (
            "- **केवल लाइव API डेटा:** सभी तापमान, पूर्वानुमान और AQI मान सीधे लाइव API से आते हैं। "
            "कोई भी नकली या यादृच्छिक संख्या नहीं दिखाई जाती।\n"
            "- **पारदर्शी नियम:** सलाह बारिश की संभावना (`>= 70%`, `< 30%`), अधिकतम तापमान (`> 40°C`) और हवा की गति (`> 20 km/h`) पर आधारित है।\n"
            "- **इकाइयाँ:** हवा की गति `m/s × 3.6` से `km/h` में और `pop × 100` से `%` में बदली जाती है।"
        ),
        "search_placeholder": "MP या भारत का शहर/जिला लिखें (जैसे: Bhopal, Indore, Sagar, Jaipur)",
        "search_button": "मौसम खोजें",
        "search_label": "शहर या जिला खोजें",
        "choose_location_label": "एक से अधिक स्थान मिले हैं। कृपया सही स्थान चुनें:",
        "location_banner_coords": "निर्देशांक",
        "location_banner_provider": "डेटा स्रोत",
        "location_banner_updated": "अंतिम अपडेट",
        "current_weather_heading": "वर्तमान मौसम",
        "feels_like": "महसूस तापमान",
        "observation_time": "अवलोकन समय",
        "humidity": "नमी (Humidity)",
        "wind_speed": "हवा की गति",
        "pressure": "वायुदाब",
        "cloud_cover": "बादल आवरण",
        "sunrise": "सूर्योदय",
        "sunset": "सूर्यास्त",
        "forecast_heading": "पाँच दिनों का मौसम पूर्वानुमान",
        "forecast_caption": "दैनिक न्यूनतम/अधिकतम तापमान, बारिश की संभावना और हवा की गति {interval} पूर्वानुमान अंतरालों से निकाली गई है।",
        "chart_heading": "5-दिवसीय तापमान ग्राफ",
        "min_temp": "न्यूनतम",
        "max_temp": "अधिकतम",
        "rain_prob": "बारिश संभावना",
        "advisory_heading": "स्मार्ट कृषि सलाह (नियम-आधारित)",
        "advisory_horizon_label": "पूर्वानुमान नियम जाँच अवधि:",
        "horizon_5d": "पूरे 5 दिन का पूर्वानुमान",
        "horizon_48h": "अगले 48 घंटे",
        "horizon_24h": "अगले 24 घंटे",
        "why_this_advice": "यह सलाह क्यों दी गई?",
        "advisory_inputs_label": "पूर्वानुमान से प्राप्त वास्तविक मान ({horizon})",
        "advisory_disclaimer": (
            "कृषि सुरक्षा सूचना: ये सरल नियम-आधारित सुझाव केवल सामान्य और शैक्षिक जानकारी के लिए हैं—यह "
            "आधिकारिक IMD चेतावनी या फसल-विशेष विशेषज्ञ सलाह का विकल्प नहीं हैं। छिड़काव या सिंचाई से पहले "
            "स्थानीय कृषि विज्ञान केंद्र (KVK) या राज्य कृषि विभाग की सलाह अवश्य देखें।"
        ),
        "aqi_heading": "वायु गुणवत्ता सूचकांक (AQI)",
        "aqi_scale_ow": "OpenWeather AQI (1–5 स्केल)",
        "aqi_scale_om": "Open-Meteo European AQI",
        "aqi_scale_note_ow": "ध्यान दें: OpenWeather 1 से 5 के स्केल (1 = अच्छा, 5 = बहुत खराब) का उपयोग करता है, जो भारत के CPCB AQI (0–500) से अलग है।",
        "aqi_scale_note_om": "ध्यान दें: Open-Meteo यूरोपीय AQI स्केल दिखाता है, जो OpenWeather (1–5) और भारत के CPCB AQI (0–500) दोनों से अलग है।",
        "pollutants_heading": "प्रदूषक स्तर (μg/m³)",
        "data_unavailable": "डेटा उपलब्ध नहीं है",
        "retry_button": "पुनः प्रयास करें",
        "use_fallback_button": "Open-Meteo लाइव बैकअप आज़माएं",
        "missing_key_banner": (
            "OpenWeather API कुंजी अभी सेट नहीं है। अपनी `.env` फ़ाइल में `OPENWEATHER_API_KEY` जोड़ें "
            "(या साइडबार में सेशन कुंजी डालें), अथवा बिना API Key के लाइव मौसम देखने के लिए नीचे Open-Meteo बैकअप चुनें।"
        ),
        "footer_source": "मुख्य स्रोत: OpenWeatherMap | वैकल्पिक बैकअप: Open-Meteo",
        "footer_accuracy": "मौसम पूर्वानुमान अनुमानित होते हैं और बदल सकते हैं; महत्वपूर्ण निर्णय के लिए आधिकारिक IMD अपडेट देखें।",
        "original_desc_note": "प्रदाता विवरण",
        "intervals_count": "{n} अंतराल",
        "err_empty_query": "कृपया खोजने के लिए शहर या जिले का नाम दर्ज करें।",
        "err_missing_api_key": "OpenWeather API कुंजी उपलब्ध नहीं है। .env कॉन्फ़िगर करें या Open-Meteo बैकअप का उपयोग करें।",
        "err_invalid_api_key": "OpenWeather ने API कुंजी अस्वीकार कर दी (HTTP 401)। कृपया कुंजी जांचें या नई कुंजी सक्रिय होने की प्रतीक्षा करें।",
        "err_rate_limit": "API सीमा पूरी हो गई है (HTTP 429)। कृपया थोड़ी देर बाद पुनः प्रयास करें।",
        "err_location_not_found": "इस नाम का कोई स्थान नहीं मिला। कृपया वर्तनी जांचें या राज्य का नाम जोड़ें (जैसे 'Sagar, MP')।",
        "err_timeout": "मौसम सेवा से उत्तर मिलने में समय समाप्त हो गया। कृपया पुनः प्रयास करें।",
        "err_network_error": "नेटवर्क त्रुटि: मौसम API से संपर्क नहीं हो पा रहा। कृपया इंटरनेट कनेक्शन जांचें।",
        "err_api_error": "मौसम सेवा से त्रुटि प्राप्त हुई।",
        "err_invalid_response": "मौसम प्रदाता से अधूरा या अनपेक्षित डेटा प्राप्त हुआ।",
    },
}

WEEKDAYS_HI: dict[str, str] = {
    "Mon": "सोमवार",
    "Tue": "मंगलवार",
    "Wed": "बुधवार",
    "Thu": "गुरुवार",
    "Fri": "शुक्रवार",
    "Sat": "शनिवार",
    "Sun": "रविवार",
}

WEATHER_CONDITION_HI: dict[str, str] = {
    "clear sky": "साफ आसमान",
    "mainly clear": "मुख्यतः साफ आसमान",
    "partly cloudy": "आंशिक बादल",
    "few clouds": "हल्के बादल",
    "scattered clouds": "बिखरे हुए बादल",
    "broken clouds": "घने आंशिक बादल",
    "overcast clouds": "घने बादल",
    "mist": "हल्का कोहरा / धुंध",
    "smoke": "धुआं / धुंध",
    "haze": "धुंध",
    "dust": "धूल भरी हवा",
    "sand": "रेत / धूल",
    "fog": "कोहरा",
    "light drizzle": "हल्की बूंदाबांदी",
    "moderate drizzle": "मध्यम बूंदाबांदी",
    "dense drizzle": "तेज बूंदाबांदी",
    "drizzle": "बूंदाबांदी",
    "light intensity drizzle": "हल्की बूंदाबांदी",
    "light rain": "हल्की बारिश",
    "moderate rain": "मध्यम बारिश",
    "heavy intensity rain": "तेज बारिश",
    "very heavy rain": "बहुत तेज बारिश",
    "extreme rain": "अत्यधिक भारी बारिश",
    "light intensity shower rain": "हल्की बौछार",
    "shower rain": "तेज बौछार",
    "light rain showers": "हल्की बारिश की बौछारें",
    "moderate rain showers": "मध्यम बारिश की बौछारें",
    "violent rain showers": "तेज मूसलाधार बौछारें",
    "thunderstorm": "आंधी और बिजली",
    "thunderstorm with light rain": "हल्की बारिश के साथ गरज-चमक",
    "thunderstorm with rain": "बारिश के साथ आंधी-तूफान",
    "thunderstorm with heavy rain": "तेज बारिश के साथ आंधी-तूफान",
    "light snow": "हल्की बर्फबारी",
    "snow": "बर्फबारी",
}

OPENWEATHER_AQI_LEVELS: dict[int, dict[str, str]] = {
    1: {"en": "Good", "hi": "अच्छा", "color": "#16A34A", "bg": "#DCFCE7"},
    2: {"en": "Fair", "hi": "संतोषजनक", "color": "#65A30D", "bg": "#ECFCCB"},
    3: {"en": "Moderate", "hi": "मध्यम", "color": "#D97706", "bg": "#FEF3C7"},
    4: {"en": "Poor", "hi": "खराब", "color": "#EA580C", "bg": "#FFEDD5"},
    5: {"en": "Very Poor", "hi": "बहुत खराब", "color": "#DC2626", "bg": "#FEE2E2"},
}


def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    """Return a localized UI string for 'en' or 'hi', falling back to English."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    template = lang_dict.get(key) or TRANSLATIONS["en"].get(key) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def translate_weekday(short_day: str, lang: str = "en") -> str:
    """Translate 3-letter English weekday abbreviation when Hindi is selected."""
    if lang == "hi":
        return WEEKDAYS_HI.get(short_day, short_day)
    return short_day


def translate_condition(description: str | None, lang: str = "en") -> str:
    """Translate weather description using maintained mapping, or label original if unmapped."""
    if not description:
        return t("data_unavailable", lang)
    cleaned = description.strip()
    if lang != "hi":
        return cleaned.title()

    mapped = WEATHER_CONDITION_HI.get(cleaned.lower())
    if mapped:
        return mapped
    return f"{t('original_desc_note', 'hi')}: {cleaned}"


def translate_error(error_code: str | None, error_detail: str | None, lang: str = "en") -> str:
    """Return user-friendly localized error text while preserving provider specifics."""
    key = f"err_{error_code}" if error_code else "err_api_error"
    base_msg = t(key, lang) if key in TRANSLATIONS["en"] else t("err_api_error", lang)
    if error_detail and error_code not in {"missing_api_key", "empty_query"}:
        return f"{base_msg} ({error_detail})"
    return base_msg


def get_openweather_aqi_meta(aqi_value: int | None, lang: str = "en") -> dict[str, str]:
    """Return label and color styling for OpenWeather AQI (1-5)."""
    if aqi_value in OPENWEATHER_AQI_LEVELS:
        info = OPENWEATHER_AQI_LEVELS[aqi_value]
        return {
            "label": info["hi"] if lang == "hi" else info["en"],
            "color": info["color"],
            "bg": info["bg"],
        }
    return {
        "label": t("data_unavailable", lang),
        "color": "#475569",
        "bg": "#E2E8F0",
    }


def get_european_aqi_meta(aqi_value: int | None, lang: str = "en") -> dict[str, str]:
    """Return label and styling for Open-Meteo European AQI (0-100+)."""
    if aqi_value is None:
        return {"label": t("data_unavailable", lang), "color": "#475569", "bg": "#E2E8F0"}
    if aqi_value <= 20:
        return {"label": "अच्छा" if lang == "hi" else "Good", "color": "#16A34A", "bg": "#DCFCE7"}
    if aqi_value <= 40:
        return {"label": "संतोषजनक" if lang == "hi" else "Fair", "color": "#65A30D", "bg": "#ECFCCB"}
    if aqi_value <= 60:
        return {"label": "मध्यम" if lang == "hi" else "Moderate", "color": "#D97706", "bg": "#FEF3C7"}
    if aqi_value <= 80:
        return {"label": "खराब" if lang == "hi" else "Poor", "color": "#EA580C", "bg": "#FFEDD5"}
    if aqi_value <= 100:
        return {"label": "बहुत खराब" if lang == "hi" else "Very Poor", "color": "#DC2626", "bg": "#FEE2E2"}
    return {"label": "अत्यंत खराब" if lang == "hi" else "Extremely Poor", "color": "#991B1B", "bg": "#FEE2E2"}

