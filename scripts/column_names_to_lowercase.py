# Column Names to Lowercase Script
## This code was created via Google AI. The purpose of this script is to reads CSV files in a folder, convert column names to lowercase, and overwrite the original files to show the lowercase column names

from pathlib import Path
import pandas as pd


def overwrite_csv_columns_to_lowercase(folder_path: str) -> None:
    """
    Reads all CSV files in a folder, converts column names to lowercase, 
    and overwrites the original files to show the lowercase column names.
    """

    target_dir = Path(folder_path)

    # Validate that the folder exists
    if not target_dir.is_dir():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    # Gather all CSV files in the directory
    csv_files = list(target_dir.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in '{folder_path}'.")
        return

    print(
        f"WARNING: This will overwrite {len(csv_files)} file(s) in place.\n"
    )

    # Process each file
    for file_path in csv_files:
        try:
            print(f"Processing: {file_path.name}")

            # 1. Read the data
            df = pd.read_csv(file_path)

            # 2. Modify headers to lowercase
            df.columns = df.columns.str.lower()

            # 3. Save directly back to the exact same file path (Overwrite)
            df.to_csv(file_path, index=False)
            print(f"-> Successfully overwritten!\n")

        except pd.errors.EmptyDataError:
            print(f"-> Skipped: {file_path.name} is empty.\n")
        except Exception as e:
            print(f"-> Error processing {file_path.name}: {e}\n")

    print("All files updated successfully!")


if __name__ == "__main__":
    # Replace this with the path to your folder
    FOLDER_TO_UPDATE = "data/"

    # Run the function
    overwrite_csv_columns_to_lowercase(FOLDER_TO_UPDATE)

