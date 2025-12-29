"""
00_load_and_clean.py

Purpose
-------
Load and clean the Individual Household Electric Power Consumption dataset.

This script:
- Loads the raw dataset from the UCI Machine Learning Repository
- Validates the expected schema
- Parses and validates datetime information
- Normalizes data types
- Handles missing values with explicit, domain-aware rules
- Flags (but does not remove) outliers
- Saves a clean, analysis-ready dataset for downstream EDA and modeling

Inputs
------
- data/individual_household_electric_power_consumption.csv (raw data)

Outputs
-------
- data/processed_power_data.csv (cleaned dataset)
- figures/outlier_frequency_by_hour.png (diagnostic visualization)

Notes
-----
- Feature engineering is intentionally deferred to a separate script.
- Outliers are flagged rather than removed to preserve real consumption behavior.
"""

# %%
# ---- LIBRARY IMPORTS ----
import pandas as pd
import matplotlib.pyplot as plt

from ucimlrepo import fetch_ucirepo
from pathlib import Path

# %%
# ---- CONFIG ----
VERBOSE = True

# %%
# ---- PATHS & SETUP ----
DATA_DIR = Path("data")
FIGURES_DIR = Path("figures")

RAW_DATA_PATH = DATA_DIR / "individual_household_electric_power_consumption.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed_power_data.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# %%
# ---- FETCH DATASET (ONLY IF NEEDED) + SAVE RAW DATA ----
if not RAW_DATA_PATH.exists():
    dataset = fetch_ucirepo(id=235)
    raw_df = pd.concat([dataset.data.features, dataset.data.targets], axis=1)
    raw_df.to_csv(RAW_DATA_PATH, index=False)
    print(f"✅ Raw data saved to: {RAW_DATA_PATH}")
else:
    print(f"ℹ️ Raw data already exists at: {RAW_DATA_PATH}")

# %%
# ---- LOAD RAW DATA ----
df = pd.read_csv(RAW_DATA_PATH, low_memory=False, na_values=["?"])
print(f"✅ Loaded raw data: {df.shape}")

# %%
# ---- INSPECTION / INITIAL EXPLORATION ----
if VERBOSE:
    print("\n--- HEAD (first 5 rows) ---")
    print(df.head())

    print("\n--- INFO ---")
    df.info()

    print("\n--- DTYPES ---")
    print(df.dtypes)

    print("\n--- MISSING VALUES (top 10) ---")
    print(df.isna().sum().sort_values(ascending=False).head(10))

    print("\n--- SUMMARY STATS ---")
    print(df.describe(include="all"))

# %%
# ---- SCHEMA VALIDATION ----
required_cols = {"Date", "Time"}
missing_required = required_cols - set(df.columns)
if missing_required:
    raise KeyError(f"Missing required columns for datetime parsing: {missing_required}")

# %%
# ---- DATETIME PARSING ----
df["Date"] = df["Date"].astype(str).str.strip()
df["Time"] = df["Time"].astype(str).str.strip()

dt_str = df["Date"] + " " + df["Time"]

# Try strict known format first (common for this dataset)
df["datetime"] = pd.to_datetime(
    dt_str,
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)

# Fallback for any remaining unparsed rows
bad_dt = df["datetime"].isna()
if bad_dt.any():
    df.loc[bad_dt, "datetime"] = pd.to_datetime(dt_str[bad_dt], dayfirst=True, errors="coerce")

missing_dt = int(df["datetime"].isna().sum())
print(f"Missing/invalid datetime entries: {missing_dt}")

# Drop invalid datetimes, drop Date/Time columns, sort and index by datetime
df = df.dropna(subset=["datetime"]).drop(columns=["Date", "Time"])
df = df.sort_values("datetime").set_index("datetime")
print(f"✅ After datetime parsing: {df.shape}")

# %%
# ---- DATA TYPE NORMALIZATION ----
# Convert all remaining columns to numeric (coerce junk to NaN)
df = df.apply(pd.to_numeric, errors="coerce")

# %%
# ---- MISSING VALUE ANALYSIS (BEFORE HANDLING) ----
missing_before = df.isna().sum().sort_values(ascending=False)
if VERBOSE:
    print("\nMissing values BEFORE handling (non-zero):")
    print(missing_before[missing_before > 0].head(20))

# %%
# ---- MISSING VALUE HANDLING ----
# Sub-metering columns (all treated equally)
sub_meter_cols = [
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]

for col in sub_meter_cols:
    if col in df.columns:
        df[f"{col}_missing"] = df[col].isna().astype(int)
        df[col] = df[col].fillna(0)

# Drop rows missing core electrical measurements
core_cols = [
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
]

rows_before = len(df)
df = df.dropna(subset=core_cols)
rows_after = len(df)

print(f"✅ Dropped rows with missing core measurements: {rows_before - rows_after:,}")
print(f"✅ Remaining rows: {rows_after:,}")

# %%
# ---- POST-CLEAN INSPECTION ----
print("✅ Post-clean dataset inspection")

if VERBOSE:
    print("\nFinal shape:")
    print(df.shape)

    print("\nFinal dtypes:")
    print(df.dtypes)

    print("\nRemaining missing values (top 10):")
    missing_after = df.isna().sum().sort_values(ascending=False)
    print(missing_after.head(10))

# %%
# ---- PREPARE FOR OUTLIER FEATURES ----
df = df.copy()

# %%
# ---- OUTLIER DETECTION (IQR + ROLLING Z-SCORE) ----
def detect_outliers_iqr(series, factor=1.5):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    return (series < lower) | (series > upper)

# Outliers are flagged (not removed) to preserve real consumption spikes for downstream analysis.
df["outlier_iqr"] = detect_outliers_iqr(df["Global_active_power"])

WINDOW = "24h"
THRESHOLD = 3

rolling_mean = df["Global_active_power"].rolling(WINDOW).mean()
rolling_std = df["Global_active_power"].rolling(WINDOW).std()
z_score = (df["Global_active_power"] - rolling_mean) / rolling_std

df["outlier_rolling_z"] = z_score.abs() > THRESHOLD

# Combined flag for convenience in EDA/modeling
df["outlier_any"] = df["outlier_iqr"] | df["outlier_rolling_z"]

print("Outlier counts:")
print("IQR outliers:", int(df["outlier_iqr"].sum()))
print("Rolling Z-score outliers:", int(df["outlier_rolling_z"].sum()))
print("Any outlier:", int(df["outlier_any"].sum()))

# %%
# ---- OUTLIER DENSITY BY HOUR ----
outliers = df[df["outlier_any"]].copy()
outliers["hour"] = outliers.index.hour

outliers["hour"].value_counts().sort_index().plot(
    kind="bar",
    figsize=(10, 4),
    title="Outlier Frequency by Hour of Day"
)

plt.xlabel("Hour of Day")
plt.ylabel("Number of Outliers")

outlier_plot_path = FIGURES_DIR / "outlier_frequency_by_hour.png"
plt.savefig(outlier_plot_path, bbox_inches="tight")
plt.show()

print(f"📈 Outlier visualization saved to: {outlier_plot_path}")

# %%
# ---- SAVE PROCESSED DATA ----
df.to_csv(PROCESSED_DATA_PATH)
print(f"✅ Processed data saved to: {PROCESSED_DATA_PATH}")