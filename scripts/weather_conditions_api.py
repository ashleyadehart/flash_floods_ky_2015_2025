# Weather Conditions API Script
# This code was generated via Open-Meteo and ChatGPT. This code was used to retrieve weather conditions for each flash flooding event in the dataset based on the event's date and location. The script uses the Open-Meteo API to fetch daily weather data, including temperature, precipitation, wind speed, etc. The retrieved weather data is then merged with the original dataset and saved as a new CSV file for further analysis.

import time
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session():
    session = requests.Session()

    retries = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    return session


def get_historical_weather_row(session, api_key, location, date_str):
    base_url = "https://api.weatherapi.com/v1/history.json"

    params = {
        "key": api_key,
        "q": f"{location}, Kentucky, USA",
        "dt": date_str
    }

    fields = [
        "MAXTEMP_F", "MINTEMP_F", "AVGTEMP_F", "MAXWIND_MPH",
        "TOTALPRECIP_IN", "AVGVIS_MILES", "AVGHUMIDITY",
        "CONDITION_TEXT", "CONDITION_CODE", "UV",
        "DAILY_WILL_IT_RAIN", "DAILY_CHANCE_OF_RAIN"
    ]

    result = {field: None for field in fields}

    try:
        response = session.get(base_url, params=params, timeout=30)

        if response.status_code != 200:
            print(f"Skipping {location} on {date_str}: API Status {response.status_code}")
            print(response.text[:300])
            return result

        data = response.json()

        forecast_day = data["forecast"]["forecastday"][0]["day"]

        result["MAXTEMP_F"] = forecast_day.get("maxtemp_f")
        result["MINTEMP_F"] = forecast_day.get("mintemp_f")
        result["AVGTEMP_F"] = forecast_day.get("avgtemp_f")
        result["MAXWIND_MPH"] = forecast_day.get("maxwind_mph")
        result["TOTALPRECIP_IN"] = forecast_day.get("totalprecip_in")
        result["AVGVIS_MILES"] = forecast_day.get("avgvis_miles")
        result["AVGHUMIDITY"] = forecast_day.get("avghumidity")
        result["CONDITION_TEXT"] = forecast_day.get("condition", {}).get("text")
        result["CONDITION_CODE"] = forecast_day.get("condition", {}).get("code")
        result["UV"] = forecast_day.get("uv")
        result["DAILY_WILL_IT_RAIN"] = forecast_day.get("daily_will_it_rain")
        result["DAILY_CHANCE_OF_RAIN"] = forecast_day.get("daily_chance_of_rain")

    except requests.exceptions.Timeout:
        print(f"Timeout for {location} on {date_str}")

    except requests.exceptions.RequestException as e:
        print(f"Request error for {location} on {date_str}: {e}")

    except KeyError as e:
        print(f"Missing expected data for {location} on {date_str}: {e}")

    except Exception as e:
        print(f"Error processing {location} on {date_str}: {e}")

    return result


def process_weather_dataset(input_csv, output_csv, api_key):
    print(f"Loading dataset: {input_csv}")
    df = pd.read_csv(input_csv)

    required_columns = ["BEGIN_LOCATION", "BEGIN_DATE"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df["BEGIN_DATE_CLEANED"] = pd.to_datetime(df["BEGIN_DATE"]).dt.strftime("%Y-%m-%d")

    session = create_session()
    collected_data = []

    print("Starting historical weather data collection...")

    for idx, row in df.iterrows():
        loc = row["BEGIN_LOCATION"]
        date_str = row["BEGIN_DATE_CLEANED"]

        print(f"Processing row {idx + 1}/{len(df)}: {loc} on {date_str}")

        weather_data = get_historical_weather_row(
            session=session,
            api_key=api_key,
            location=loc,
            date_str=date_str
        )

        collected_data.append(weather_data)

        # Save progress every 50 rows
        if (idx + 1) % 50 == 0:
            temp_weather_df = pd.DataFrame(collected_data)
            temp_final_df = pd.concat([df.iloc[:idx + 1].reset_index(drop=True), temp_weather_df], axis=1)
            temp_final_df.drop(columns=["BEGIN_DATE_CLEANED"]).to_csv(output_csv, index=False)
            print(f"Progress saved through row {idx + 1}")

        time.sleep(1)

    weather_df = pd.DataFrame(collected_data)
    final_df = pd.concat([df.reset_index(drop=True), weather_df], axis=1)

    final_df = final_df.drop(columns=["BEGIN_DATE_CLEANED"])

    final_df.to_csv(output_csv, index=False)
    print(f"Successfully saved complete dataset to: {output_csv}")


if __name__ == "__main__":
    API_KEY = "YOUR API KEY GOES HERE"
    INPUT_FILE = "data/processed/flash_floods_ky_2015_2025_cleaned.csv"
    OUTPUT_FILE = "data/raw/flash_floods_ky_weather_conditions.csv"

    process_weather_dataset(INPUT_FILE, OUTPUT_FILE, API_KEY)