# Smart Weather Forecasting and Agriculture Advisory System for MP Region using OpenWeather API

> **Project Blueprint / Synopsis / Implementation Guide**\
> Level: Beginner-friendly college mini project\
> Frontend: Streamlit\
> Language: Python\
> Main data source: OpenWeather API\
> Charts: Matplotlib\
> Optional fallback: Open-Meteo API\
> Target users: General public and farmers, with an initial focus on
> Madhya Pradesh (MP)

------------------------------------------------------------------------

## 1. Project Overview

Build a simple, attractive, responsive weather dashboard that retrieves
**real weather data from an API** and converts it into
easy-to-understand Hindi or English guidance.

This is not just a temperature app. It combines: - Current weather
information. - A five-day forecast with a temperature graph. - Simple
rule-based agriculture and daily-life advisory. - Air Quality Index
(AQI). - Hindi / English language support. - City and district search
across India, with MP shown as the default region.

**Important:** Never display random, hard-coded, or fabricated weather
values. If an API request fails, show a clear error or "Data
unavailable" message. Do not silently replace live data with sample
values.

## 2. Problem Statement

Weather applications often show technical values such as temperature,
humidity, wind speed, and rainfall probability. Many users---especially
farmers---may not know what action to take based on those values.
Information may also be difficult to understand when it is presented
only in English.

The proposed system will fetch live weather and forecast data and
present it in simple Hindi or English. It will apply transparent,
rule-based conditions to generate general suggestions such as whether
rain may affect spraying, whether high temperatures may increase crop
water needs, or whether strong winds may affect field activities.

## 3. Objectives

1.  Display current weather for a searched city or district.
2.  Provide a five-day forecast and temperature trend graph.
3.  Generate simple agriculture advisories from actual forecast values.
4.  Display current AQI and available pollutant details.
5.  Provide a Hindi / English language toggle.
6.  Support locations across Indian states using city/district name and
    geocoding---not a fixed list of MP cities only.
7.  Keep the application easy to install, explain, and demonstrate in a
    college viva.

## 4. Main Features

### Feature 1 --- Current Weather Dashboard

After a user searches for a location, show: - Current temperature (°C) -
Feels-like temperature - Weather condition and icon - Humidity (%) -
Wind speed (km/h) - Atmospheric pressure (hPa) - Cloud cover (%) -
Sunrise and sunset (local time, where available) - Last updated /
observation time

Use clean metric cards with icons, readable labels, and a dark-blue /
sky-blue weather theme.

### Feature 2 --- Five-Day Forecast

Show a five-day forecast with: - Date and weekday - Minimum and maximum
temperature - Weather condition - Rain probability, where returned by
the provider - Wind speed

Add a Matplotlib line chart for daily minimum and maximum temperature.
Build daily values from the forecast API's timestamps; do not invent
missing dates or values. If the API only provides 3-hour forecast
intervals, clearly describe the chart as daily values derived from those
intervals.

### Feature 3 --- Smart Agriculture Advisory

This is the project's main problem-solving feature. Use actual forecast
data to generate rule-based suggestions.

Suggested beginner rules:

  -----------------------------------------------------------------------
  Actual API condition                Example advisory
  ----------------------------------- -----------------------------------
  Rain probability is 70% or higher   "बारिश की संभावना अधिक है। दवा का
  in the relevant forecast period     छिड़काव करने से पहले स्थानीय मौसम अपडेट
                                      देखें; बारिश से छिड़काव प्रभावित हो सकता
                                      है।"

  Forecast maximum temperature is     "गर्मी अधिक रहने की संभावना है। फसल की
  above 40°C                          जरूरत और स्थानीय कृषि सलाह के अनुसार सुबह
                                      या शाम सिंचाई पर विचार करें।"

  Forecast wind speed is above 20     "हवा तेज हो सकती है। छिड़काव या पौधों से
  km/h                                जुड़े काम से पहले हवा की स्थिति जांचें।"

  Rain probability is low and wind is "मौसम के उपलब्ध पूर्वानुमान में बारिश की
  not strong                          संभावना कम है। खेत का काम करने से पहले
                                      ताजा अपडेट देखें।"
  -----------------------------------------------------------------------

Implementation notes: - OpenWeather forecast `pop` is a fraction from
`0` to `1`; convert it to a percentage using `pop * 100`. - OpenWeather
wind speed is normally returned in metres/second. Convert it to km/h
using `wind_speed_ms * 3.6`. - Use forecast values for the relevant
future period, not just the current weather. - Display the exact reason
for every advisory, for example: "Rain probability: 82%". - If a
required field is missing, do not trigger that rule. Show "Insufficient
forecast data" instead. - Avoid presenting these simple rules as expert
crop-specific advice. Add a note that farmers should follow local
agriculture department / KVK guidance for crop-specific decisions.

### Feature 4 --- Air Quality Index (AQI)

Use OpenWeather Air Pollution API to show: - AQI category / level -
PM2.5 - PM10 - NO₂, O₃, SO₂ and CO when returned

OpenWeather's AQI scale is **1 to 5**, not India's CPCB AQI scale of 0
to 500. Label it clearly as **OpenWeather AQI (1--5)**. Do not call it
"CPCB AQI" or compare the numbers directly with Indian AQI categories.

### Feature 5 --- Hindi / English Language Toggle

Add a visible language switch: - English - हिंदी

Translate the interface labels, advisory messages, buttons, and help
text using a small local dictionary in Python. Weather condition
descriptions can be translated using a maintained mapping where
possible; otherwise show the provider's original description with a
clear label.

### Feature 6 --- Search Locations Across India

-   Add a location search box.
-   Use OpenWeather Geocoding API to convert the searched city/district
    into latitude and longitude.
-   Include India as the country filter where appropriate.
-   Display the resolved location name and state/country details
    returned by geocoding.
-   Make Madhya Pradesh the default example region, with Bhopal as the
    initial demo location.
-   The search should not be limited to Bhopal, Indore, or a hard-coded
    list. It should work for locations in other Indian states when the
    provider returns a valid geocoding result.
-   If multiple places have the same name, show a small selection list
    with state/country details so the user can choose the correct one.

------------------------------------------------------------------------

## 5. Recommended APIs and Free Data Sources

### Primary: OpenWeatherMap

Website: https://openweathermap.org/

Create a free account and generate an API key:
https://home.openweathermap.org/api_keys

Use these endpoints:

  ---------------------------------------------------------------------------------------------
  Purpose                             Endpoint
  ----------------------------------- ---------------------------------------------------------
  City name to coordinates            `https://api.openweathermap.org/geo/1.0/direct`

  Current weather                     `https://api.openweathermap.org/data/2.5/weather`

  Five-day / three-hour forecast      `https://api.openweathermap.org/data/2.5/forecast`

  Air pollution / AQI                 `https://api.openweathermap.org/data/2.5/air_pollution`
  ---------------------------------------------------------------------------------------------

The OpenWeather free access page currently lists Current Weather, 5 Day
/ 3 Hour Forecast, Air Pollution, and Geocoding. Check the provider's
current limits and terms before deployment: - API overview:
https://openweathermap.org/api - Pricing and free access:
https://openweathermap.org/price - API guide:
https://openweathermap.org/guide

**Do not assume every OpenWeather endpoint is free.** Use only the
endpoints listed in the active free plan. Do not build the project
around One Call or paid daily forecast features unless the account
explicitly includes them.

### Optional fallback: Open-Meteo

Website: https://open-meteo.com/

Open-Meteo offers forecast and geocoding services without an API key for
non-commercial use, subject to its usage limits and attribution
requirements.

-   Forecast documentation: https://open-meteo.com/en/docs
-   Geocoding documentation:
    https://open-meteo.com/en/docs/geocoding-api
-   Air quality documentation:
    https://open-meteo.com/en/docs/air-quality-api

Use this only as an optional fallback or comparison source. Clearly
label which provider supplied the data. Do not mix values from different
providers in one card without identifying the source.

### Optional official India source: IMD

-   IMD API portal: https://api.imd.gov.in/public/
-   API reference: https://api.imd.gov.in/public/api_reference.html

The IMD API reference lists weather forecasts, district-wise warnings,
rainfall data, and Agromet Advisory APIs. Explore registration and
access requirements before depending on these endpoints. If access is
unavailable, the application should continue using the primary weather
provider and clearly label its rule-based suggestions as general
guidance---not official IMD advice.

------------------------------------------------------------------------

## 6. Tech Stack

  Part                   Technology
  ---------------------- ------------------------------------
  Programming language   Python
  User interface         Streamlit
  API requests           requests
  Data handling          pandas
  Graphs                 Matplotlib
  Date and time          Python datetime / zoneinfo
  Configuration          python-dotenv or Streamlit secrets
  Main weather data      OpenWeather API
  Optional fallback      Open-Meteo API

Keep the implementation beginner-friendly. Do not add machine learning,
a database, login, or a complex backend unless the teacher specifically
asks for them.

## 7. Application Flow

1.  User opens the Streamlit application.
2.  User selects Hindi or English.
3.  User enters a city or district, such as Bhopal.
4.  Python sends the location to the OpenWeather Geocoding API.
5.  The API returns coordinates and location details.
6.  Python uses those coordinates to request current weather, five-day
    forecast, and air pollution data.
7.  The application validates the returned JSON data.
8.  Pandas prepares forecast values and Matplotlib creates the
    temperature graph.
9.  The advisory module checks real forecast values against the defined
    rules.
10. Streamlit displays the dashboard, forecast, AQI, and advisory.

### Simple system diagram

``` text
User
  |
  v
Streamlit Interface
  |
  v
Python Application
  |
  +----> OpenWeather Geocoding API
  |             |
  |             v
  |        Latitude / Longitude
  |
  +----> Current Weather API
  |
  +----> 5-Day Forecast API
  |
  +----> Air Pollution API
                |
                v
        JSON Weather Data
                |
                v
      Data Processing + Rules
                |
        +-------+-------+
        |               |
        v               v
   Matplotlib       Hindi / English
     Graph            Advisory
        |               |
        +-------+-------+
                |
                v
        Streamlit Dashboard
```

## 8. Interface / UI Design

Create a polished but simple interface suitable for a college project
presentation.

### Design direction

-   Modern weather dashboard.
-   Deep navy / blue background with light cards.
-   Sky-blue accent colour.
-   Clear typography and consistent spacing.
-   Rounded metric cards with subtle shadows.
-   Responsive layout for laptop and mobile screens.
-   Avoid excessive animations and unnecessary complex components.

### Suggested screen layout

1.  **Header:** Project name, short tagline, language toggle.
2.  **Search section:** City/district input and Search button.
3.  **Current weather hero card:** Location, temperature, condition and
    weather icon.
4.  **Weather metrics:** Humidity, wind, pressure, feels-like, sunrise
    and sunset.
5.  **Forecast section:** Five-day cards and temperature graph.
6.  **Agriculture advisory:** Clear alert cards with "Why this advice?"
    showing the real API value and rule.
7.  **Air quality section:** OpenWeather AQI scale and pollutant values.
8.  **Footer:** Data source, last updated time, API attribution, and
    advisory disclaimer.

Do not show blank white boxes when data is missing. Use a neat "Data
unavailable" placeholder that matches the theme.

## 9. Suggested Project Folder Structure

``` text
smart-weather-agriculture/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── services/
│   ├── geocoding.py
│   ├── weather_api.py
│   └── air_quality.py
│
├── utils/
│   ├── advisory.py
│   ├── translations.py
│   └── charts.py
│
└── README.md
```

For a very small first version, it is acceptable to start with `app.py`
and split files into modules later. Keep API requests and advisory rules
separate where practical.

## 10. API Key and Security

1.  Create an OpenWeather account and generate an API key.
2.  Store the key in a local `.env` file or Streamlit secrets.
3.  Never paste the real key directly into Python source code.
4.  Add `.env` to `.gitignore`.
5.  Provide `.env.example` with a placeholder only.

Example `.env.example`:

``` env
OPENWEATHER_API_KEY=PASTE_YOUR_OWN_KEY_HERE
```

For Streamlit secrets, use `.streamlit/secrets.toml` locally and do not
upload the real file to a public repository.

## 11. Data Accuracy and Error Handling

This is a key project requirement.

-   Every displayed weather value must come from a successful API
    response.
-   Never generate random temperatures, humidity, rainfall, wind, or AQI
    values.
-   Do not hard-code Bhopal weather as if it were live data.
-   Show the selected city/district and provider name.
-   Show the API observation or forecast timestamp.
-   Use proper units: °C, %, km/h, hPa, and the provider's AQI scale.
-   Handle invalid city names, network errors, API rate limits, invalid
    API keys, and missing fields.
-   If the API is unavailable, show an error message and a Retry option.
-   Cache successful responses briefly to reduce unnecessary requests,
    but display the time of the last successful update.
-   Do not describe forecasts as 100% accurate. Weather forecasts are
    estimates and can change.
-   A successful geocoding result does not guarantee that every weather
    endpoint will return data; handle each endpoint independently.
-   If a location is ambiguous, ask the user to choose the correct
    state/country result.

## 12. Synopsis Content

### Objective

To develop a user-friendly weather forecasting and agriculture advisory
system that provides real-time weather information, five-day forecasts,
air quality information, and simple Hindi/English advisories for users,
especially farmers in Madhya Pradesh.

### Methodology

The system uses API integration. The user searches for a city or
district, the application obtains its geographical coordinates through a
geocoding API, and then fetches current weather, forecast, and air
pollution data. Python processes the JSON responses, generates a
temperature graph, and applies predefined rules to display simple
advisories.

### Advantages

-   No costly weather sensors are required for the basic application.
-   Live data is fetched from weather APIs instead of using random
    sample values.
-   The interface can be used for locations across India where the
    provider has coverage.
-   Hindi language support makes the information easier to understand.
-   Rule-based advisory logic is simple, transparent, and easy to
    explain.
-   The project can be built without machine learning.

### Future Scope

-   SMS and WhatsApp weather alerts.
-   Voice-based Hindi weather updates.
-   Crop-specific advisories developed with agriculture experts.
-   Integration with official IMD district warnings and Agromet
    advisories, subject to access.
-   Saved favourite locations.
-   Rainfall history and seasonal comparisons.
-   A mobile-friendly progressive web application.
-   Optional multilingual support for more Indian languages.

## 13. Viva Explanation

**Q: What is the main purpose of this project?**\
A: The project does not only display temperature. It fetches actual
weather data and converts forecast values into simple guidance that
general users and farmers can understand.

**Q: How does the application get weather data?**\
A: It sends HTTP requests to OpenWeather APIs. The APIs return JSON
responses, which Python processes and displays through Streamlit.

**Q: How does the agriculture advisory work?**\
A: It uses predefined if/else conditions. For example, if forecast rain
probability is above 70%, it displays a rain-related caution. The
condition and actual value are shown to the user.

**Q: Is this machine learning?**\
A: No. The first version uses a transparent rule-based system. Machine
learning is not required.

**Q: Does it work only in Madhya Pradesh?**\
A: MP is the project's initial focus and default demonstration region.
City/district geocoding allows users to search other Indian states too,
provided the API returns a valid location and weather response.

**Q: Is the data 100% accurate?**\
A: No weather forecast can be guaranteed to be 100% accurate. The
application displays data from the selected provider and shows its
update time. Users should check official local warnings before making
important decisions.

**Q: What is the difference between weather data and agriculture
advisory?**\
A: Weather data contains measurements and forecast values. The advisory
module applies simple rules to those values and explains possible
actions in everyday language.

## 14. Development Plan

Build the project in this order:

-   [ ] Create the Python virtual environment.
-   [ ] Install Streamlit, requests, pandas, matplotlib, and
    python-dotenv.
-   [ ] Create an OpenWeather API key.
-   [ ] Implement city/district geocoding.
-   [ ] Fetch and display current weather.
-   [ ] Fetch the five-day / three-hour forecast.
-   [ ] Prepare daily minimum and maximum temperatures.
-   [ ] Draw the Matplotlib temperature graph.
-   [ ] Fetch Air Pollution API data and label its AQI scale correctly.
-   [ ] Implement the rule-based agriculture advisory.
-   [ ] Add Hindi / English translations.
-   [ ] Apply the final dashboard design.
-   [ ] Test locations from multiple Indian states.
-   [ ] Test invalid city names, missing fields, network failures, and
    invalid API keys.
-   [ ] Verify that no random or fake values are displayed.
-   [ ] Prepare screenshots and explain the system flow for the viva.

## 15. Requirements Installation

Suggested `requirements.txt`:

``` text
streamlit
requests
pandas
matplotlib
python-dotenv
```

Run:

``` bash
pip install -r requirements.txt
streamlit run app.py
```

## 16. Final Scope and Important Limitations

Keep the first version small and reliable: - One Streamlit
application. - OpenWeather as the main weather provider. - Current
weather, five-day forecast, AQI, graph, language toggle, and rule-based
advisory. - City/district search across India through geocoding. - No
login, database, payment system, or machine learning in version 1.

**Agriculture safety note:** The advisory is educational and
general-purpose. It is not a substitute for crop-specific advice from a
Krishi Vigyan Kendra (KVK), state agriculture department, or qualified
agricultural expert. Never recommend pesticide application or irrigation
solely from a simple weather threshold.

**Data-source note:** OpenWeather data is provider-supplied
forecast/current weather data, not a guarantee of direct
government-satellite observations. Display the source and timestamp
honestly. Use official IMD warnings/advisories when available and
clearly identify them as official data.

------------------------------------------------------------------------

## Reference Links

1.  OpenWeather API overview --- https://openweathermap.org/api
2.  OpenWeather free plan and pricing ---
    https://openweathermap.org/price
3.  OpenWeather API guide --- https://openweathermap.org/guide
4.  Open-Meteo --- https://open-meteo.com/
5.  Open-Meteo forecast documentation --- https://open-meteo.com/en/docs
6.  Open-Meteo Air Quality API ---
    https://open-meteo.com/en/docs/air-quality-api
7.  India Meteorological Department API portal ---
    https://api.imd.gov.in/public/
8.  IMD API reference ---
    https://api.imd.gov.in/public/api_reference.html
9.  Streamlit documentation --- https://docs.streamlit.io/
