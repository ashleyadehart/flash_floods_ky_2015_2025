# Weather Conditions API Script
# This code was generated via Open-Meteo and ChatGPT. This code was used to retrieve weather conditions for each flash flooding event in the dataset based on the event's date and location. The script uses the Open-Meteo API to fetch daily weather data, including temperature, precipitation, wind speed, and more. The retrieved weather data is then merged with the original dataset and saved as a new CSV file for further analysis.

# ---------------------------
# Import Libraries
# ---------------------------
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import time

# ---------------------------
# Setup Open-Meteo Client
# ---------------------------
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# ---------------------------
# Load CSV
# ---------------------------
df = pd.read_csv(
    "data/processed/flash_floods_ky_2015_2025_cleaned.csv"
)

# ---------------------------
# Function to Get Weather
# ---------------------------
def get_weather(row):

    lat = row["BEGIN_LAT"]
    lon = row["BEGIN_LON"]

    # Convert date to YYYY-MM-DD
    date = pd.to_datetime(row["BEGIN_DATE"]).strftime("%Y-%m-%d")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date,
        "end_date": date,
        "daily": [
            "temperature_2m_mean",
            "sunrise",
            "sunset",
            "precipitation_sum",
            "rain_sum",
            "precipitation_hours",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
            "temperature_2m_max",
            "temperature_2m_min"
        ],
        "timezone": "America/New_York"
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        daily = response.Daily()
        return {
            "TEMP_MEAN": daily.Variables(0).ValuesAsNumpy()[0],
            "SUNRISE": daily.Variables(1).ValuesInt64AsNumpy()[0],
            "SUNSET": daily.Variables(2).ValuesInt64AsNumpy()[0],
            "PRECIP_SUM": daily.Variables(3).ValuesAsNumpy()[0],
            "RAIN_SUM": daily.Variables(4).ValuesAsNumpy()[0],
            "PRECIP_HOURS": daily.Variables(5).ValuesAsNumpy()[0],
            "MAX_WIND": daily.Variables(6).ValuesAsNumpy()[0],
            "MAX_GUST": daily.Variables(7).ValuesAsNumpy()[0],
            "WIND_DIRECTION": daily.Variables(8).ValuesAsNumpy()[0],
            "TEMP_MAX": daily.Variables(9).ValuesAsNumpy()[0],
            "TEMP_MIN": daily.Variables(10).ValuesAsNumpy()[0]
        }

    except Exception as e:
        print(f"Error row: {e}")
        return {
            "TEMP_MEAN": None,
            "SUNRISE": None,
            "SUNSET": None,
            "PRECIP_SUM": None,
            "RAIN_SUM": None,
            "PRECIP_HOURS": None,
            "MAX_WIND": None,
            "MAX_GUST": None,
            "WIND_DIRECTION": None,
            "TEMP_MAX": None,
            "TEMP_MIN": None
        }

# ---------------------------
# Loop Through Rows
# ---------------------------
weather_results = []

for i, row in df.iterrows():
    weather = get_weather(row)
    weather_results.append(weather)

    print(f"Processed row {i}")

    time.sleep(0.2)

# ---------------------------
# Merge Weather Data
# ---------------------------
weather_df = pd.DataFrame(weather_results)
df = pd.concat([df, weather_df], axis=1)

# ---------------------------
# Save
# ---------------------------
df.to_csv(
    "data/raw/flash_floods_ky_weather_conditions.csv",
    index=False
)

print("Finished!")