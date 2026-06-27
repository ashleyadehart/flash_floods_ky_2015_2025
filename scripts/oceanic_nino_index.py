from datetime import datetime
from pathlib import Path
import pandas as pd

# Paths to local input and output files
INPUT_FILE = "data/processed/flash_floods_ky_event_info.csv"
OUTPUT_FILE = "data/processed/flash_floods_ky_oni_results.csv"
DATE_COLUMN = "BEGIN_DATE"  

# Point directly to downloaded backup file
LOCAL_BACKUP_FILE = "data/raw/oni_backup.txt"


def parse_oni_text(text_data: str) -> pd.DataFrame:
    """Parses raw NOAA ASCII text tables into a clean DataFrame."""
    lines = text_data.strip().split("\n")
    header = lines[0].split()
    data_rows = [line.split() for line in lines[1:]]

    df_oni = pd.DataFrame(data_rows, columns=header)
    df_oni["YR"] = df_oni["YR"].astype(int)
    df_oni["ANOM"] = df_oni["ANOM"].astype(float)

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

    # Create datetime timestamp set to the first day of the month
    df_oni["date"] = pd.to_datetime(
        df_oni.apply(
            lambda row: datetime(int(row["YR"]), int(row["month"]), 1), axis=1
        )
    )

    # Classify ENSO Phase based on standard +/- 0.5°C threshold
    def classify_enso(anom: float) -> str:
        if anom >= 0.5:
            return "El Nino"
        elif anom <= -0.5:
            return "La Nina"
        return "Neutral"

    df_oni["enso_phase"] = df_oni["ANOM"].apply(classify_enso)
    df_oni = df_oni[["date", "ANOM", "enso_phase"]].rename(
        columns={"ANOM": "oni_anomaly"}
    )
    return df_oni.sort_values("date").reset_index(drop=True)


def load_local_oni(backup_filename: str) -> pd.DataFrame:
    """Reads the local ONI backup file and prepares it for merging."""
    backup_path = Path(backup_filename)

    if not backup_path.exists():
        print(
            f"[-] Critical Error: Local file '{backup_filename}' not found."
        )
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

    # 1. Verify and load flash flood dataset
    if not input_path.exists():
        print(f"[-] Error: Input file '{input_path}' does not exist.")
        return

    try:
        flood_df = load_dataset(input_path)
    except Exception as e:
        print(f"[-] Failed to read input file: {e}")
        return

    if DATE_COLUMN not in flood_df.columns:
        print(
            f"[-] Error: Target column '{DATE_COLUMN}' not found in input file."
        )
        print(f"Available columns: {list(flood_df.columns)}")
        return

    # 2. Parse the dates and cache the original file ordering
    flood_df[DATE_COLUMN] = pd.to_datetime(flood_df[DATE_COLUMN])
    original_order = flood_df.index
    flood_df = flood_df.sort_values(DATE_COLUMN)

    # 3. Process the local offline text index
    try:
        oni_df = load_local_oni(LOCAL_BACKUP_FILE)
    except Exception as e:
        print(f"[-] Processing local index failed: {e}")
        return

    # 4. Perform the closest preceding historical match (as of date merge)
    print("[+] Merging flash flood rows with historical climate phases...")
    enriched_df = pd.merge_asof(
        flood_df,
        oni_df,
        left_on=DATE_COLUMN,
        right_on="date",
        direction="backward",
    )

    # Clean up tracking date duplicates and restore initial dataset order
    if "date" in enriched_df.columns:
        enriched_df = enriched_df.drop(columns=["date"])
    enriched_df = enriched_df.loc[original_order].reset_index(drop=True)

    # 5. Output file generation
    print(f"[+] Writing enriched dataset out to: {output_path.name}")
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_dataset(enriched_df, output_path)
        print("[+] Process completed successfully!")
    except Exception as e:
        print(f"[-] Failed to write file: {e}")


if __name__ == "__main__":
    main()
