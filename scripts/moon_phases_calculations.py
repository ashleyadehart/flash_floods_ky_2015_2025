# Moon Phases API Script
## This script was generated via Google AI. The purpose of this script was to calculate the moon phase and illumination percentage for each flash flooding event in the dataset based on the event's date and location. The script uses the `ephem` library to perform astronomical calculations and adds two new columns to the dataset: `MOON_PHASE_NAME` and `MOON_ILLUMINATION_PCT`.

from datetime import datetime
from pathlib import Path
import ephem
import pandas as pd

# CONFIGURATION & CONSTANTS
INPUT_FILE = Path("data/processed/flash_floods_ky_weather_conditions_cleaned.csv")
OUTPUT_FILE = Path("data/processed/flash_floods_ky_moon_data.csv")


def calculate_local_moon(row: pd.Series) -> pd.Series:
    """Calculates moon phase name and illumination percentage for a given row."""
    try:
        date_obj = datetime.strptime(row["BEGIN_DATE"], "%Y-%m-%d")
        
        observer = ephem.Observer()
        observer.lat = str(row["BEGIN_LAT"])
        observer.lon = str(row["BEGIN_LON"])
        observer.date = date_obj
        
        moon = ephem.Moon()
        moon.compute(observer)
        
        illumination = moon.phase / 100.0
        
        # Get moon age to determine waxing vs waning (0 to ~29.53 days)
        prev_new = ephem.previous_new_moon(observer.date)
        next_new = ephem.next_new_moon(observer.date)
        lunation_age = (observer.date - prev_new) * 29.53 / (next_new - prev_new)
        
        # Map illumination and age to a local human-readable phase
        if illumination < 0.03:
            phase_name = "New Moon"
        elif illumination > 0.97:
            phase_name = "Full Moon"
        elif lunation_age < 14.77:
            if illumination < 0.45:
                phase_name = "Waxing Crescent"
            elif illumination < 0.55:
                phase_name = "First Quarter"
            else:
                phase_name = "Waxing Gibbous"
        else:
            if illumination > 0.55:
                phase_name = "Waning Gibbous"
            elif illumination > 0.45:
                phase_name = "Third Quarter"
            else:
                phase_name = "Waning Crescent"
                
        return pd.Series({
            "MOON_PHASE_NAME": phase_name,
            "MOON_ILLUMINATION_PCT": round(illumination * 100, 2)
        })
        
    except Exception as e:
        return pd.Series({
            "MOON_PHASE_NAME": f"Error: {str(e)}",
            "MOON_ILLUMINATION_PCT": None
        })


def main():
    """Main execution function to load data, process moon metrics, and save."""
    if not INPUT_FILE.is_file():
        print(f"[Error] Source file not found at: {INPUT_FILE.resolve()}")
        print("Please verify your working directory and try again.")
        return

    print(f"Loading dataset from: {INPUT_FILE.name}...")
    df = pd.read_csv(INPUT_FILE)
    
    print("Calculating moon phases and illumination across all entries...")
    # Process row-by-row via apply map
    moon_data = df.apply(calculate_local_moon, axis=1)
    df[["MOON_PHASE_NAME", "MOON_ILLUMINATION_PCT"]] = moon_data
    
    # Ensure the parent directory exists before writing output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"File processed successfully! Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
