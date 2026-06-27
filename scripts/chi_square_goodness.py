# Chi-Square Goodness of Fit Script
## This code was generated via Google AI. The purpose of this script was to conduct a Chi-Square Goodness of Fit test on the moon data gathered for each flash flooding event.

from pathlib import Path
import pandas as pd
from scipy.stats import chisquare

# Define the relative path from the project root
INPUT_FILE = Path("data/processed/flash_floods_ky_moon_data.csv")


def analyze_moon_illumination(file_path):
    """Loads flash flood data and performs a Chi-Square Goodness-of-Fit test."""
    df = pd.read_csv(file_path)

    # Create moon illumination bins
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    labels = [
        "0-10%", "10-20%", "20-30%", "30-40%", "40-50%",
        "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"
    ]

    df["illumination_bin"] = pd.cut(
        df["MOON_ILLUMINATION_PCT"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    # Count observed events in each bin
    observed = df["illumination_bin"].value_counts().sort_index()

    # Calculate expected counts assuming equal distribution
    expected = [len(df) / len(observed)] * len(observed)

    # Run Chi-Square Goodness-of-Fit Test
    chi2, p_value = chisquare(f_obs=observed, f_exp=expected)

    # Print results
    print("Observed Counts:")
    print(observed)
    print("\nExpected Counts:")
    print(expected)
    print(f"\nChi-Square Statistic: {chi2:.4f}")
    print(f"P-Value: {p_value:.6f}")


if __name__ == "__main__":
    if INPUT_FILE.is_file():
        analyze_moon_illumination(INPUT_FILE)
    else:
        print(f"[Error] Could not find the file at: {INPUT_FILE.resolve()}")
        print("Please ensure you are running this script from the project root folder.")
