"""
01_eda.py

Purpose
-------
Explore temporal patterns, variability, and anomalous behavior in household
electricity consumption to inform feature engineering and modeling decisions.

Summary of Findings
-------------------
- Household electricity consumption exhibits strong diurnal patterns, with
  average usage lowest overnight and peaking during morning and evening hours,
  consistent with typical household routines.

- Electricity usage distributions are highly right-skewed and multi-modal,
  indicating distinct operating states such as baseline consumption, moderate
  usage, and high-demand periods rather than a single typical level.

- Extreme consumption values are rare but structured, comprising approximately
  5% of observations and clustering at specific times of day rather than
  occurring randomly.

- Outlier frequency peaks during evening hours, reinforcing the interpretation
  that outliers reflect behavior-driven events (e.g., cooking, heating, appliance
  usage) rather than sensor noise or data quality issues.

- Daily and weekly trend analysis shows stable long-term behavior with short-term
  variability, suggesting that recent usage history and short-horizon temporal
  features will be informative for modeling.

- Appliance-level sub-metering variables show meaningful relationships with total
  household power consumption, supporting their inclusion as explanatory features
  in downstream analysis.

Notes
-----
- This script performs exploratory analysis only and does not modify the dataset.
- Feature engineering decisions based on these findings are implemented in
  `02_features.py`.
"""

# %%
# ---- LIBRARY IMPORTS ----
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# ---- CONFIG ----
VERBOSE = True

# %%
# ---- PATHS & SETUP ----
DATA_DIR = Path("data")
FIGURES_DIR = Path("figures")

INPUT_PATH = DATA_DIR / "processed_power_data.csv"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# %%
# ---- LOAD CLEANED DATA ----
df = pd.read_csv(
    INPUT_PATH,
    parse_dates=["datetime"],
    index_col="datetime"
).sort_index()

print(f"✅ Loaded cleaned data: {df.shape}")

# %%
# ---- BASIC SANITY CHECKS ----
if VERBOSE:
    print("\n--- DATAFRAME INFO ---")
    df.info()

    print("\n--- SUMMARY STATISTICS ---")
    print(df.describe())

    print("\n--- MISSING VALUES PER COLUMN ---")
    print(df.isnull().sum().sort_values(ascending=False).head(15))

    print("\n--- DATAFRAME HEAD ---")
    print(df.head())

# %%
# ---- DISTRIBUTION ANALYSIS ----
if VERBOSE:
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns

    binary_cols = [c for c in numeric_cols if df[c].nunique() <= 2]
    cont_cols = [c for c in numeric_cols if c not in binary_cols]

    # Continuous distributions
    for col in cont_cols:
        plt.figure(figsize=(8, 4))
        sns.histplot(df[col].dropna(), bins=50, kde=True)
        plt.title(f"Distribution of {col}")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.show()

    # Binary distributions (count plots)
    for col in binary_cols:
        plt.figure(figsize=(6, 3))
        sns.countplot(x=df[col])
        plt.title(f"Counts of {col}")
        plt.xlabel(col)
        plt.ylabel("Count")
        plt.show()

# %%
# ---- TEMPORAL PATTERN ANALYSIS ----
if VERBOSE:
    daily_df = df.resample("D").mean(numeric_only=True)

    plt.figure(figsize=(12, 6))
    plt.plot(daily_df.index, daily_df["Global_active_power"], label="Daily Avg Global Active Power")
    plt.title("Daily Average Global Active Power Over Time")
    plt.xlabel("Date")
    plt.ylabel("Global Active Power (kW)")
    plt.legend()

    fig_path = FIGURES_DIR / "daily_avg_global_active_power.png"
    plt.savefig(fig_path, bbox_inches="tight")
    plt.show()
    print(f"📈 Saved: {fig_path}")

    weekly_df = df.resample("W").mean(numeric_only=True)

    plt.figure(figsize=(12, 6))
    plt.plot(weekly_df.index, weekly_df["Global_active_power"], label="Weekly Avg Global Active Power")
    plt.title("Weekly Average Global Active Power Over Time")
    plt.xlabel("Date")
    plt.ylabel("Global Active Power (kW)")
    plt.legend()

    fig_path = FIGURES_DIR / "weekly_avg_global_active_power.png"
    plt.savefig(fig_path, bbox_inches="tight")
    plt.show()
    print(f"📈 Saved: {fig_path}")

# %%
# ---- AVERAGE POWER BY HOUR OF DAY ----
hourly_mean = df.groupby(df.index.hour)["Global_active_power"].mean()

plt.figure(figsize=(10, 4))
plt.plot(hourly_mean.index, hourly_mean.values)
plt.title("Average Global Active Power by Hour of Day")
plt.xlabel("Hour of Day")
plt.ylabel("Global Active Power (kW)")

fig_path = FIGURES_DIR / "avg_global_active_power_by_hour.png"
plt.savefig(fig_path, bbox_inches="tight")
plt.show()
print(f"📈 Saved: {fig_path}")

# %%
# ---- OUTLIER FREQUENCY BY HOUR OF DAY ----
if "outlier_any" not in df.columns:
    raise KeyError("Column 'outlier_any' not found. Run 00_load_and_clean.py to generate outlier flags.")

outliers = df[df["outlier_any"]].copy()
outliers["hour"] = outliers.index.hour

plt.figure(figsize=(10, 4))
sns.countplot(x="hour", data=outliers)
plt.title("Outlier Frequency by Hour of Day")
plt.xlabel("Hour of Day")
plt.ylabel("Number of Outliers")

fig_path = FIGURES_DIR / "outlier_frequency_by_hour.png"
plt.savefig(fig_path, bbox_inches="tight")
plt.show()
print(f"📈 Saved: {fig_path}")