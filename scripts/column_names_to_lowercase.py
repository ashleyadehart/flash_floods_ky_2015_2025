# Column Names to Lowercase Script 
## This code was created via Claude Code. 
## The purpose of this code is to read CSV files in a folder, convert column names to lowercase, and overwrite the original files to show the lowercase column names

import csv
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


def overwrite_csv_columns_to_lowercase(folder_path: Path) -> None:
    """
    Reads all CSV files in a folder, converts the header row to lowercase,
    and overwrites the original files in place.

    Uses the `csv` module instead of pandas so files are streamed row-by-row
    rather than fully loaded, parsed, type-inferred, and re-serialized just
    to change the header. This avoids pandas' dtype-inference side effects
    (e.g. int->float coercion on NaN, stripped leading zeros, reformatted
    dates) and is significantly cheaper for large files.

    Each file is written to a temporary file first and then atomically
    swapped into place with os.replace(), so a crash or interruption
    mid-write can't leave a truncated or corrupted file behind.
    """

    # Case-insensitive match so "*.CSV" / "*.Csv" aren't silently skipped
    csv_files = [p for p in folder_path.glob("*") if p.suffix.lower() == ".csv"]
    if not csv_files:
        print(f"No CSV files found in '{folder_path}'.")
        return

    print(f"WARNING: This will overwrite {len(csv_files)} file(s) in place.\n")

    succeeded = 0
    skipped = 0
    failed = 0

    for file_path in csv_files:
        print(f"Processing: {file_path.name}")
        tmp_path = None
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                try:
                    header = next(reader)
                except StopIteration:
                    # Empty file - nothing to rewrite
                    print(f"-> Skipped: {file_path.name} is empty.\n")
                    skipped += 1
                    continue

                lowered_header = [col.lower() for col in header]

                # Write to a temp file in the same directory (so os.replace
                # stays on the same filesystem and is atomic), then swap in.
                with NamedTemporaryFile(
                    mode="w",
                    newline="",
                    encoding="utf-8",
                    dir=file_path.parent,
                    prefix=f".{file_path.stem}_",
                    suffix=".tmp",
                    delete=False,
                ) as outfile:
                    tmp_path = Path(outfile.name)
                    writer = csv.writer(outfile)
                    writer.writerow(lowered_header)
                    for row in reader:
                        writer.writerow(row)

            os.replace(tmp_path, file_path)
            print("-> Successfully overwritten!\n")
            succeeded += 1

        except Exception as e:
            print(f"-> Error processing {file_path.name}: {e}\n")
            failed += 1
            # Clean up the temp file if something went wrong after it was created
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()

    print(
        f"Done: {succeeded} updated, {skipped} skipped (empty), "
        f"{failed} failed, out of {len(csv_files)} total."
    )


def main():
    # Accept an optional folder path as a CLI arg; default to "data/"
    folder_arg = sys.argv[1] if len(sys.argv) > 1 else "data/"
    folder_to_update = Path(folder_arg)

    if not folder_to_update.is_dir():
        print(f"Error: Folder '{folder_to_update}' does not exist.")
        return

    overwrite_csv_columns_to_lowercase(folder_to_update)


if __name__ == "__main__":
    main()