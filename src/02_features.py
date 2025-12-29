"""
02_features.py

Purpose
-------
Create modeling-ready features from the cleaned household electricity dataset.

This script:
- Loads the cleaned dataset produced by `00_load_and_clean.py`
- Engineers time-based, lag, and rolling-window features to capture temporal context
  and short-term consumption dynamics informed by EDA
- Drops rows created with NaNs due to lag/rolling operations
- Saves a feature dataset for downstream modeling

Inputs
------
- data/processed_power_data.csv

Outputs
-------
- data/feature_power_data.csv

Notes
-----
- Scaling and train/validation splitting are deferred to `03_modeling.py`
  to prevent data leakage and keep model-specific steps in the modeling stage.
"""

# %%
# ---- LIBRARY IMPORTS ----
from pathlib import Path
import pandas as pd

# %%
# ---- PATHS & SETUP ----
DATA_DIR = Path("data")
INPUT_PATH = DATA_DIR / "processed_power_data.csv"
OUTPUT_PATH = DATA_DIR / "feature_power_data.csv"

# %%
# ---- LOAD CLEANED DATA ----
df = pd.read_csv(INPUT_PATH, parse_dates=["datetime"], index_col="datetime").sort_index()
print(f"✅ Loaded cleaned data: {df.shape}")

# %%
# ---- FEATURE ENGINEERING ----
# Time-based features
df["hour"] = df.index.hour
df["day_of_week"] = df.index.dayofweek
df["month"] = df.index.month
df["is_weekend"] = (df.index.dayofweek >= 5).astype(int)

# Lag features (minutes)
for lag in [1, 5, 15, 60]:
    df[f"gap_lag_{lag}"] = df["Global_active_power"].shift(lag)

# Rolling features (minutes) – window sizes chosen to capture short-term behavior
for win in [15, 60]:
    df[f"gap_roll_mean_{win}"] = df["Global_active_power"].rolling(win).mean()
    df[f"gap_roll_std_{win}"] = df["Global_active_power"].rolling(win).std()

# Retain outlier flags from preprocessing as contextual features
# (outliers represent real usage behavior, not data errors)

# %%
# ---- DROP NA FROM FEATURE CREATION ----
# Lag/rolling create NaNs at the start; drop them once at the end
rows_before = len(df)
df = df.dropna()
print(f"✅ Dropped {rows_before - len(df):,} rows due to lag/rolling NaNs")
print(f"✅ Feature dataset shape: {df.shape}")

# %%
# ---- SAVE FEATURE DATA ----
df.to_csv(OUTPUT_PATH)
print(f"✅ Saved feature dataset to: {OUTPUT_PATH}")