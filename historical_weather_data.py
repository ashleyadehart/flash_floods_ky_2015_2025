import pandas as pd
import requests
import time

# Load dataset
df = pd.read_csv("data/processed/county_city_date_counts.csv")

# Visual Crossing Setup
BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
API_KEY = "REMOVED"

# Function to get weather for one row
def get_weather(row):

    date = row["BEGIN_DATE"]
    lat = row["BEGIN_LAT"]
    lon = row["BEGIN_LON"]

    location = f"{lat},{lon}"
    url = f"{BASE_URL}{location}/{date}/{date}"

    params = {
        "unitGroup": "us",
        "include": "days",
        "key": API_KEY,
        "contentType": "json"
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            if "days" in data and len(data["days"]) > 0:
                day = data["days"][0]

                return {
                    "temp": day.get("temp"),
                    "precip": day.get("precip"),
                    "humidity": day.get("humidity"),
                    "windspeed": day.get("windspeed")
                }

        return {
            "temp": None,
            "precip": None,
            "humidity": None,
            "windspeed": None
        }

    except Exception as e:
        print(f"Error processing row: {e}")
        return {
            "temp": None,
            "precip": None,
            "humidity": None,
            "windspeed": None
        }


# Create new columns
df["TEMP"] = None
df["PRECIP"] = None
df["HUMIDITY"] = None
df["WINDSPEED"] = None

# Loop through dataframe
for i, row in df.iterrows():

    weather = get_weather(row)

    df.at[i, "TEMP"] = weather["temp"]
    df.at[i, "PRECIP"] = weather["precip"]
    df.at[i, "HUMIDITY"] = weather["humidity"]
    df.at[i, "WINDSPEED"] = weather["windspeed"]

    print(f"Processed row {i}")

    # Rate limiting
    time.sleep(1)

# Save enriched dataset
df.to_csv("data/processed/county_city_date_weather_enriched.csv", index=False)

print("Done! File saved as county_city_date_weather_enriched.csv")