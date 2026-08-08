import os
import pandas as pd

csv_files = [
    "data/processed/flash_floods_ky_event_info.csv",
    "data/processed/flash_floods_ky_impact_data.csv",
    "data/processed/flash_floods_ky_moon_sun_data.csv",
    "data/processed/flash_floods_ky_nlcd_data.csv",
    "data/processed/flash_floods_ky_oni_data.csv",
    "data/processed/flash_floods_ky_soil_data.csv",
    "data/processed/flash_floods_ky_weather_conditions_data.csv"
]

valid_files = [
    file for file in csv_files
    if os.path.exists(file)
]

missing_files = [
    file for file in csv_files
    if not os.path.exists(file)
]

if missing_files:
    print("Warning: The following files were not found:")

    for file in missing_files:
        print(f"  - {file}")

if not valid_files:
    print("Error: None of the specified CSV files were found.")

else:
    print(f"Found {len(valid_files)} CSV files.\n")

    combined_df = pd.read_csv(valid_files[0])

    print(
        f"Loaded: {os.path.basename(valid_files[0])}"
    )

    print(
        f"Rows: {len(combined_df):,} | "
        f"Columns: {len(combined_df.columns):,}\n"
    )

    for file in valid_files[1:]:

        print(f"Merging: {os.path.basename(file)}")

        df = pd.read_csv(file)

        combined_df = combined_df.merge(
            df,
            on="event_id",
            how="left"
        )

        print(
            f"Current rows: {len(combined_df):,} | "
            f"Current columns: {len(combined_df.columns):,}\n"
        )

    output_filename = (
        "data/processed/flash_floods_ky_combined_data.csv"
    )

    combined_df.to_csv(
        output_filename,
        index=False
    )

    print("=" * 60)
    print("COMBINATION COMPLETE")
    print("=" * 60)

    print(f"Final rows:    {len(combined_df):,}")
    print(f"Final columns: {len(combined_df.columns):,}")
    print(f"Output file:   {output_filename}")