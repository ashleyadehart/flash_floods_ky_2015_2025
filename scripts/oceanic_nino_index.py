# Oceanic Nino Index Script
## This code was generated via Claude Code. 
## The purpose of this code is to gather ONI data for every row in the flash_floods_ky_event_info.csv file for further analysis.

import io
from pathlib import Path
import numpy as np
import pandas as pd

# Paths to local input and output files
INPUT_FILE = "data/processed/flash_floods_ky_event_info.csv"
OUTPUT_FILE = "data/processed/flash_floods_ky_oni_data.csv"
DATE_COLUMN = "begin_date"

# Point directly to downloaded backup file
LOCAL_BACKUP_FILE = "data/raw/oni_backup.txt"


def parse_oni_text(text_data: str) -> pd.DataFrame:
    """Parses raw NOAA ASCII text tables into a clean DataFrame."""
    df_oni = pd.read_csv(
        io.StringIO(text_data.strip()),
        sep=r"\s+",
        dtype={"YR": int, "ANOM": float},
    )

    # Map 3-letter seasons to a central calendar month index
    season_to_month = {
        "DJF": 1,
        "JFM": 2,
        "FMA": 3,
        "MAM": 4,
        "AMJ": 5,
        "MJJ": 6,
        "JJA": 7,
        "JAS": 8,
        "ASO": 9,
        "SON": 10,
        "OND": 11,
        "NDJ": 12,
    }
    df_oni["month"] = df_oni["SEAS"].map(season_to_month)

    # Create datetime timestamp set to the first day of the month (vectorized)
    df_oni["date"] = pd.to_datetime(
        dict(year=df_oni["YR"], month=df_oni["month"], day=1)
    )

    # Classify ENSO Phase based on standard +/- 0.5°C threshold (vectorized)
    df_oni["enso_phase"] = np.select(
        [df_oni["ANOM"] >= 0.5, df_oni["ANOM"] <= -0.5],
        ["El Nino", "La Nina"],
        default="Neutral",
    )

    # Modified to include 'SEAS' and rename it to 'oni_season'
    df_oni = df_oni[["date", "SEAS", "ANOM", "enso_phase"]].rename(
        columns={"SEAS": "oni_season", "ANOM": "oni_anomaly"}
    )

    return df_oni.sort_values("date").reset_index(drop=True)


def load_local_oni(backup_filename: str) -> pd.DataFrame:
    """Reads the local ONI backup file and prepares it for merging."""
    backup_path = Path(backup_filename)
    if not backup_path.exists():
        print(f"[-] Critical Error: Local file '{backup_filename}' not found.")
        print(
            "Please ensure you have placed 'oni_backup.txt' in the same folder as this script."
        )
        raise FileNotFoundError(f"Missing local file: {backup_filename}")

    print(f"[+] Reading local climate data from: {backup_path.name}")
    with open(backup_path, "r", encoding="utf-8") as f:
        backup_text = f.read()

    return parse_oni_text(backup_text)


def load_dataset(file_path: Path) -> pd.DataFrame:
    """Helper to load either a CSV or Excel file."""
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(file_path)
    elif suffix in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format '{suffix}'. Use CSV or Excel.")


def save_dataset(df: pd.DataFrame, file_path: Path) -> None:
    """Helper to save the dataframe as either a CSV or Excel file."""
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(file_path, index=False)
    elif suffix in [".xlsx", ".xls"]:
        df.to_excel(file_path, index=False)
    else:
        raise ValueError(f"Unsupported file format '{suffix}'. Use CSV or Excel.")


def main():
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    # Verify and load flash flood dataset
    if not input_path.exists():
        print(f"[-] Error: Input file '{input_path}' does not exist.")
        return

    try:
        flood_df = load_dataset(input_path)
    except (ValueError, OSError) as e:
        print(f"[-] Failed to read input file: {e}")
        return

    if DATE_COLUMN not in flood_df.columns:
        print(f"[-] Error: Target column '{DATE_COLUMN}' not found in input file.")
        print(f"Available columns: {list(flood_df.columns)}")
        return

    # Parse the dates and sort chronologically for the as-of merge
    flood_df[DATE_COLUMN] = pd.to_datetime(flood_df[DATE_COLUMN])
    flood_df = flood_df.sort_values(DATE_COLUMN)

    # Process the local offline text index
    try:
        oni_df = load_local_oni(LOCAL_BACKUP_FILE)
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"[-] Processing local index failed: {e}")
        return

    # Perform the closest preceding historical match (as of date merge)
    print("[+] Merging flash flood rows with historical climate phases...")
    enriched_df = pd.merge_asof(
        flood_df,
        oni_df,
        left_on=DATE_COLUMN,
        right_on="date",
        direction="backward",
    )

    # Clean up tracking date duplicates and restore original file order.
    # sort_values preserves the original index labels, so sorting the index
    # back is equivalent to (and simpler than) tracking/restoring it manually.
    if "date" in enriched_df.columns:
        enriched_df = enriched_df.drop(columns=["date"])
    enriched_df = enriched_df.sort_index().reset_index(drop=True)

    # Keep only the identifier column, year column, and the newly added ONI columns
    keep_columns = ["event_id", "oni_season", "year", "oni_anomaly", "enso_phase"]
    missing_columns = [c for c in keep_columns if c not in enriched_df.columns]
    if missing_columns:
        print(f"[-] Error: Expected column(s) not found: {missing_columns}")
        print(f"Available columns: {list(enriched_df.columns)}")
        return
    enriched_df = enriched_df[keep_columns]

    # Output file generation
    print(f"[+] Writing enriched dataset out to: {output_path.name}")
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_dataset(enriched_df, output_path)
        print("[+] Process completed successfully!")
    except (ValueError, OSError) as e:
        print(f"[-] Failed to write file: {e}")


if __name__ == "__main__":
    main()