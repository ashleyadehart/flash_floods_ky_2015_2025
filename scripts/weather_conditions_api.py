# Weather Conditions API Script 
## This code was generated via Weather API and Claude Code. 
## The purpose of this code is to retrieve weather conditions for each flash flooding event in the dataset based on the event's date and location. 

import os
import time
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# CONFIGURATION & CONSTANTS
load_dotenv()

# API configuration
WEATHER_API_URL = "https://api.weatherapi.com/v1/history.json"
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]

# File paths
INPUT_FILE = "data/processed/flash_floods_ky_2015_2025_cleaned.csv"
OUTPUT_FILE = "data/raw/flash_floods_ky_weather_conditions.csv"

# Request configuration
MAX_RETRIES = 5
BACKOFF_FACTOR = 2
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 1

# HTTP status codes that should trigger a retry
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

# HTTP methods that are safe to retry
RETRY_METHODS = ["GET"]

# Save progress after this many rows
PROGRESS_SAVE_INTERVAL = 50

# Weather fields to collect from the API
WEATHER_FIELDS = [
    "maxtemp_f",
    "mintemp_f",
    "avgtemp_f",
    "maxwind_mph",
    "totalprecip_in",
    "avgvis_miles",
    "avghumidity",
    "uv",
    "daily_will_it_rain",
    "daily_chance_of_rain"
]


def create_session():
    session = requests.Session()

    retries = Retry(
        total=MAX_RETRIES,
        connect=MAX_RETRIES,
        read=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUS_CODES,
        allowed_methods=RETRY_METHODS
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    return session


def get_historical_weather_row(session, api_key, location, date_str):
    params = {
        "key": api_key,
        "q": f"{location}, Kentucky, USA",
        "dt": date_str
    }

    result = {field: None for field in WEATHER_FIELDS}
    result.update({
        "condition_text": None,
        "condition_code": None
    })

    try:
        response = session.get(
            WEATHER_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            print(
                f"Skipping {location} on {date_str}: "
                f"API Status {response.status_code}"
            )
            print(response.text[:300])
            return result

        forecast_day = response.json()["forecast"]["forecastday"][0]["day"]

        for field in WEATHER_FIELDS:
            result[field] = forecast_day.get(field)

        condition = forecast_day.get("condition", {})

        result["condition_text"] = condition.get("text")
        result["condition_code"] = condition.get("code")

    except requests.exceptions.Timeout:
        print(f"Timeout for {location} on {date_str}")

    except requests.exceptions.RequestException as e:
        print(f"Request error for {location} on {date_str}: {e}")

    except KeyError as e:
        print(f"Missing expected data for {location} on {date_str}: {e}")

    except Exception as e:
        print(f"Error processing {location} on {date_str}: {e}")

    return result


def _build_final_df(df, collected_data, n_rows):
    weather_df = pd.DataFrame(collected_data)

    final_df = pd.concat(
        [
            df.iloc[:n_rows].reset_index(drop=True),
            weather_df
        ],
        axis=1
    )

    return final_df.drop(columns=["begin_date_cleaned"])


def process_weather_dataset(input_csv, output_csv, api_key):
    print(f"Loading dataset: {input_csv}")

    df = pd.read_csv(input_csv)

    required_columns = [
        "begin_location",
        "begin_date"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df["begin_date_cleaned"] = (
        pd.to_datetime(df["begin_date"])
        .dt.strftime("%Y-%m-%d")
    )

    session = create_session()
    collected_data = []

    print("Starting historical weather data collection...")

    for idx, row in df.iterrows():
        loc = row["begin_location"]
        date_str = row["begin_date_cleaned"]

        print(
            f"Processing row {idx + 1}/{len(df)}: "
            f"{loc} on {date_str}"
        )

        collected_data.append(
            get_historical_weather_row(
                session,
                api_key,
                loc,
                date_str
            )
        )

        # Save progress periodically
        if (idx + 1) % PROGRESS_SAVE_INTERVAL == 0:
            _build_final_df(
                df,
                collected_data,
                idx + 1
            ).to_csv(
                output_csv,
                index=False
            )

            print(f"Progress saved at row {idx + 1}")

        time.sleep(REQUEST_DELAY)

    final_df = _build_final_df(
        df,
        collected_data,
        len(df)
    )

    final_df.to_csv(
        output_csv,
        index=False
    )

    print(f"Saved: {output_csv}")


def main():
    process_weather_dataset(
        INPUT_FILE,
        OUTPUT_FILE,
        WEATHER_API_KEY
    )


if __name__ == "__main__":
    main()