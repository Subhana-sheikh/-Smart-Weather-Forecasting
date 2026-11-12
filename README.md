# Smart Weather Forecasting & Agriculture Advisory System (MP & India)

A clean, responsive **Streamlit** weather intelligence and rule-based agriculture advisory dashboard built in **Python** using the **OpenWeatherMap API** (with an optional **Open-Meteo** live fallback). Designed for the general public and farmers—with **Madhya Pradesh (Bhopal)** as the default region and pan-India city/district search—converting real-time weather and 5-day forecast data into transparent **English / हिंदी** guidance.

---

## Key Features

- **Current Weather Dashboard**: Live temperature (`°C`), feels-like temperature, humidity (`%`), wind speed (`km/h`), atmospheric pressure (`hPa`), cloud cover (`%`), sunrise/sunset local times, weather icons, and observation timestamp.
- **Five-Day Forecast & Matplotlib Graph**: Daily min/max temperatures, weather conditions, rain probability (`%`), and peak wind speed (`km/h`) derived strictly from the provider's 3-hour (or hourly) forecast timestamps, visualized with a Matplotlib trend chart.
- **Rule-Based Smart Agriculture Advisory**: Transparent `if/else` thresholds evaluating forecast rain probability, max temperature, and wind speed across 24h, 48h, or 5-day windows—always showing the exact API value and trigger timestamp under **"Why this advice?"**.
- **Air Quality Index (AQI)**: Displays **OpenWeather AQI (1–5 scale)** alongside `PM2.5`, `PM10`, `NO₂`, `O₃`, `SO₂`, and `CO` (`μg/m³`), clearly distinguishing the 1–5 scale from India's CPCB AQI (0–500).
- **Bilingual UI (`English` / `हिंदी`)**: Instant toggle translating UI labels, weekdays, weather descriptions, AQI categories, errors, and farmer advisories.
- **Pan-India Geocoding Search**: Supports cities and districts across India with multi-match disambiguation (state/country/coordinates) and quick demo shortcuts for MP & nearby cities.
- **Zero Fabricated Data**: Never displays random or hard-coded weather values; failed API calls show localized error messages, `"Data unavailable"`, and a Retry option.

---

## Agriculture Advisory Rules

| Forecast Condition | Trigger Threshold | Guidance Summary |
| --- | --- | --- |
| High Rain Probability | `rain_prob >= 70%` | Caution before spraying pesticides/fertilizers; rain may wash off or reduce effectiveness |
| High Temperature | `max_temp > 40°C` | Consider early morning or evening irrigation based on crop needs and local guidance |
| Strong Wind | `wind_speed > 20 km/h` | Check wind conditions before spraying or carrying out delicate field work |
| Low Rain & Calm Wind | `rain_prob < 30%` and `wind_speed <= 20 km/h` | Favorable window with low rain probability; check latest updates before field work |
| Missing Forecast Field | Field is `None` / absent | Rule is skipped and `"Insufficient forecast data"` is shown honestly |

---

## Tech Stack

| Component | Technology |
| --- | --- |
| Language | Python 3 |
| Frontend UI | Streamlit |
| HTTP Client | `requests` |
| Data Processing | `pandas` |
| Visualization | `matplotlib` |
| Configuration | `python-dotenv` / Streamlit secrets |
| Weather APIs | OpenWeatherMap (Primary) + Open-Meteo (Optional Fallback) |

---

## Folder Structure

```text
WeatherAgricultureProject/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
├── services/
│   ├── __init__.py
│   ├── http_client.py
│   ├── geocoding.py
│   ├── weather_api.py
│   └── air_quality.py
├── utils/
│   ├── __init__.py
│   ├── advisory.py
│   ├── translations.py
│   └── charts.py
├── tests/
│   └── test_project.py
├── Smart_Weather_Agriculture_Advisory_Project_Blueprint.md
└── README.md
```

---

## Setup & Running Locally

### 1. Clone the repository & set up virtual environment

```powershell
git clone https://github.com/Subhana-sheikh/-Smart-Weather-Forecasting.git
cd -Smart-Weather-Forecasting
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure your OpenWeather API key

1. Create a free API key at <https://home.openweathermap.org/api_keys>.

2. Copy `.env.example` to `.env`:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Add your key in `.env`:

   ```env
   OPENWEATHER_API_KEY=your_actual_openweather_api_key
   ```

> **Note:** Never commit `.env` or `.streamlit/secrets.toml` to Git (both are ignored in `.gitignore`). You can also switch the sidebar **Weather Data Provider** to **Open-Meteo (Fallback - No Key Needed)** to explore live data immediately without an API key.

### 3. Run the Streamlit app

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

### 4. Run tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

---

## Disclaimers

- **Agriculture Safety**: Rule-based advisories here are general educational guidance only—not official IMD warnings or crop-specific advice. Farmers should follow local **Krishi Vigyan Kendra (KVK)**, State Agriculture Department, or IMD Agromet advisories.
- **Forecast Accuracy**: Weather forecasts are provider-supplied estimates subject to change; always verify official local warnings before critical decisions.
