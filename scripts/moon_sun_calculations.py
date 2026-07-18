# Moon & Sun Calculations API Script
## This script was generated via Google AI Mode. 
## The purpose of this code is to calculate moon phases, illumination percentages, and sun data for each flash flooding event in the dataset based on the event's date and location.

from datetime import datetime
from pathlib import Path
import math
import ephem
import pandas as pd

# CONFIGURATION & CONSTANTS
INPUT_FILE = Path("data/processed/flash_floods_ky_event_info.csv")
OUTPUT_FILE = Path("data/processed/flash_floods_ky_moon_sun_data.csv")


def calculate_local_astro_data(row: pd.Series) -> pd.Series:
    """Calculates sun/moon position, sunrise/sunset, moon phase, and illumination."""
    try:
        date_obj = datetime.strptime(row["begin_date"], "%Y-%m-%d")
        
        # Initialize common observer
        observer = ephem.Observer()
        observer.lat = str(row["begin_lat"])
        observer.lon = str(row["begin_lon"])
        observer.date = date_obj
        
        # --- 1. SUN CALCULATIONS ---
        sun = ephem.Sun()
        sun.compute(observer)
        
        sun_alt_deg = math.degrees(sun.alt)
        sun_az_deg = math.degrees(sun.az)
        
        # Reset observer date to start of day to accurately catch rise/set
        observer.date = date_obj.date() 
        try:
            sunrise = observer.next_rising(sun)
            sunrise_str = sunrise.datetime().strftime("%Y-%m-%d %H:%M:%S")
        except (ephem.CircumpolarError, ephem.AlwaysUpError):
            sunrise_str = "Sun always up"
        except ephem.NeverUpError:
            sunrise_str = "Sun never rises"

        try:
            sunset = observer.next_setting(sun)
            sunset_str = sunset.datetime().strftime("%Y-%m-%d %H:%M:%S")
        except (ephem.CircumpolarError, ephem.AlwaysUpError):
            sunset_str = "Sun always up"
        except ephem.NeverUpError:
            sunset_str = "Sun never sets"

        # --- 2. MOON CALCULATIONS ---
        # Reset observer back to target datetime for exact position metrics
        observer.date = date_obj
        moon = ephem.Moon()
        moon.compute(observer)
        
        # Extract moon spatial coordinates relative to observer horizon
        moon_alt_deg = math.degrees(moon.alt)
        moon_az_deg = math.degrees(moon.az)
        
        illumination = moon.phase / 100.0
        
        # Determine waxing vs waning
        prev_new = ephem.previous_new_moon(observer.date)
        next_new = ephem.next_new_moon(observer.date)
        lunation_age = (observer.date - prev_new) * 29.53 / (next_new - prev_new)
        
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
            "sun_altitude_deg": round(sun_alt_deg, 2),
            "sun_azimuth_deg": round(sun_az_deg, 2),
            "sunrise_utc": sunrise_str,
            "sunset_utc": sunset_str,
            "moon_altitude_deg": round(moon_alt_deg, 2),
            "moon_azimuth_deg": round(moon_az_deg, 2),
            "moon_phase_name": phase_name,
            "moon_illumination_pct": round(illumination * 100, 2)
        })
        
    except Exception as e:
        return pd.Series({
            "sun_altitude_deg": None,
            "sun_azimuth_deg": None,
            "sunrise_utc": f"Error: {str(e)}",
            "sunset_utc": f"Error: {str(e)}",
            "moon_altitude_deg": None,
            "moon_azimuth_deg": None,
            "moon_phase_name": f"Error: {str(e)}",
            "moon_illumination_pct": None
        })


def main():
    """Main execution function to load data, process astro metrics, and save."""
    if not INPUT_FILE.is_file():
        print(f"[Error] Source file not found at: {INPUT_FILE.resolve()}")
        print("Please verify your working directory and try again.")
        return

    print(f"Loading dataset from: {INPUT_FILE.name}...")
    df = pd.read_csv(INPUT_FILE)
    
    # Force all incoming columns to lowercase (e.g., event_id, begin_date, begin_lat, begin_lon)
    df.columns = df.columns.str.lower()
    
    print("Calculating combined sun and moon profiles across all entries...")
    # Map row elements into consolidated metrics
    astro_data = df.apply(calculate_local_astro_data, axis=1)
    
    target_cols = [
        "sun_altitude_deg", "sun_azimuth_deg", "sunrise_utc", "sunset_utc",
        "moon_altitude_deg", "moon_azimuth_deg", "moon_phase_name", "moon_illumination_pct"
    ]
    df[target_cols] = astro_data
    
    # Filter the dataframe to isolate only the lowercase event identifier and astro data
    keep_cols = ["event_id"] + target_cols
    output_df = df[keep_cols]
    
    # Ensure the parent directory exists before writing output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_FILE, index=False)
    print(f"File processed successfully! Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()