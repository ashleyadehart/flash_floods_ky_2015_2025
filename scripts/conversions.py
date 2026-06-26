# Conversions Python Script
## This code was generated via ChatGPT. This code was used to convert existing variables such as temperature, precipitation, etc., along with creating new variables such as DAYLIGHT_HOURS, HEAVY_RAIN_FLAG, RAIN_TO_PRECIP_RATIO, LARGE_TEMP_SWING, and WIND_DIRECTION_CARDINAL.

import pandas as pd
import numpy as np

INPUT_FILE = "../data/processed/flash_floods_ky_weather_conditions_cleaned.csv"
OUTPUT_FILE = "../data/processed/flash_floods_ky_weather_conditions_converted.csv"

# -----------------------------------
# Load CSV
# -----------------------------------
df = pd.read_csv(INPUT_FILE)

# -----------------------------------
# Convert wind degrees to cardinal directions
# -----------------------------------
def degrees_to_cardinal(deg):
    if pd.isna(deg):
        return np.nan

    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[round(deg / 45) % 8]

# ===================================
# DATE / TIME CONVERSIONS
# ===================================

# Convert event dates
df["BEGIN_DATE"] = pd.to_datetime(
    df["BEGIN_DATE"],
    errors="coerce"
)

df["END_DATE"] = pd.to_datetime(
    df["END_DATE"],
    errors="coerce"
)

# Convert Unix timestamps → datetime
df["SUNRISE_DT"] = pd.to_datetime(
    df["SUNRISE"],
    unit="s",
    errors="coerce"
)

df["SUNSET_DT"] = pd.to_datetime(
    df["SUNSET"],
    unit="s",
    errors="coerce"
)

# Calculate daylight hours
df["DAYLIGHT_HOURS"] = (
    (df["SUNSET_DT"] - df["SUNRISE_DT"])
    .dt.total_seconds()
    / 3600
)

# Format BEGIN_TIME / END_TIME
for col in ["BEGIN_TIME", "END_TIME"]:
    df[col] = (
        df[col]
        .fillna(0)
        .astype(int)
        .astype(str)
        .str.zfill(4)
    )

# ===================================
# TEMPERATURE CONVERSIONS
# ===================================

temperature_columns = [
    "TEMP_MEAN",
    "TEMP_MAX",
    "TEMP_MIN"
]

for col in temperature_columns:
    df[f"{col}_F"] = (
        df[col] * 9/5
    ) + 32

df["TEMP_RANGE_F"] = (
    df["TEMP_MAX_F"] - df["TEMP_MIN_F"]
)

# ===================================
# PRECIPITATION CONVERSIONS
# ===================================

precip_columns = [
    "PRECIP_SUM",
    "RAIN_SUM"
]

for col in precip_columns:
    df[f"{col}_IN"] = (
        df[col] / 25.4
    )

# Heavy rainfall flag
# 2+ inches in a day = heavy rainfall indicator
df["HEAVY_RAIN_FLAG"] = np.where(
    df["PRECIP_SUM_IN"] >= 2,
    1,
    0
)

# ===================================
# WIND CONVERSIONS
# ===================================

wind_columns = [
    "MAX_WIND",
    "MAX_GUST"
]

for col in wind_columns:
    df[f"{col}_MPH"] = (
        df[col] * 0.621371
    )

# Cardinal direction
df["WIND_DIRECTION_CARDINAL"] = (
    df["WIND_DIRECTION"]
    .apply(degrees_to_cardinal)
)

# ===================================
# OPTIONAL DERIVED VARIABLES
# ===================================

# Large temperature swing flag
df["LARGE_TEMP_SWING"] = np.where(
    df["TEMP_RANGE_F"] >= 20,
    1,
    0
)

# ===================================
# SAVE OUTPUT
# ===================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Finished processing.")
print("Saved as:", OUTPUT_FILE)