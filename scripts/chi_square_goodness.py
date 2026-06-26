# Chi-Square Goodness of Fit Script
## This code was generated via Google AI. The purpose of this script was to conduct a Chi-Square Goodness of Fit test on the moon data gathered for each flash flooding event.

import pandas as pd

import pandas as pd
from scipy.stats import chisquare

# Load your dataset
df = pd.read_csv(
    r"C:\Users\msash\Projects\flash_floods_ky_2015_2025\data\processed\flash_floods_ky_weather_conditions_moon_data.csv"
)

# Create moon illumination bins
bins = [0,10,20,30,40,50,60,70,80,90,100]

labels = [
    "0-10%",
    "10-20%",
    "20-30%",
    "30-40%",
    "40-50%",
    "50-60%",
    "60-70%",
    "70-80%",
    "80-90%",
    "90-100%"
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
chi2, p_value = chisquare(
    f_obs=observed,
    f_exp=expected
)

print("Observed Counts:")
print(observed)

print("\nExpected Counts:")
print(expected)

print(f"\nChi-Square Statistic: {chi2:.4f}")
print(f"P-Value: {p_value:.6f}")