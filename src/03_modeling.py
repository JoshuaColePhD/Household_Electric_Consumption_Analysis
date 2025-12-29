"""
03_modeling.py

Purpose
-------
Train and evaluate baseline and ML models to forecast household electricity consumption
across multiple forecast horizons.

This script:
- Loads the feature dataset produced by `02_features.py`
- Creates forecasting targets (predict Global_active_power at t + horizon)
- Splits data into train/validation sets using a time-based split
- Trains baseline and ML models (with scaling where appropriate)
- Evaluates models with MAE, RMSE, and R²
- Saves evaluation metrics to disk

Inputs
------
- data/feature_power_data.csv

Outputs
-------
- data/model_metrics_by_horizon.csv

Notes
-----
- Scaling is performed inside a sklearn Pipeline to avoid data leakage.
- Random Forest training can be expensive on very large datasets; sampling is provided.
"""

# %%
# ---- LIBRARY IMPORTS ----
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# %%
# ---- CONFIG ----
VERBOSE = True

HORIZONS_MINUTES = [1, 15, 60]   # evaluate multiple horizons
TRAIN_FRACTION = 0.80            # time-based split fraction

# Random Forest can be heavy: sample training data for speed
TRAIN_SAMPLE_FRAC = 0.10         # 10% of train set (set to 1.0 to use all)
RF_ENABLED = True

RANDOM_STATE = 42

# %%
# ---- PATHS ----
DATA_DIR = Path("data")
INPUT_PATH = DATA_DIR / "feature_power_data.csv"
METRICS_PATH = DATA_DIR / "model_metrics_by_horizon.csv"

# %%
# ---- LOAD FEATURE DATA ----
df = pd.read_csv(INPUT_PATH, parse_dates=["datetime"], index_col="datetime").sort_index()
print(f"✅ Loaded feature data: {df.shape}")

if VERBOSE:
    print("Index monotonic increasing:", df.index.is_monotonic_increasing)
    print("Start:", df.index.min(), "End:", df.index.max())

# %%
# ---- EVALUATION HELPER ----
def evaluate_regression(model_name: str, horizon: int, y_true: pd.Series, y_pred: np.ndarray) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = float(np.sqrt(mse))
    r2 = r2_score(y_true, y_pred)
    return {
        "horizon_minutes": horizon,
        "model": model_name,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }

all_results = []

# %%
# ---- MODELING LOOP OVER HORIZONS ----
for HORIZON_MINUTES in HORIZONS_MINUTES:
    print("\n" + "=" * 72)
    print(f"⏱️  Horizon: {HORIZON_MINUTES} minute(s)")
    print("=" * 72)

    # ---- DEFINE TARGET (FORECASTING) ----
    # Predict Global_active_power at t + HORIZON_MINUTES.
    # Remove current Global_active_power from X to avoid trivial leakage.
    y = df["Global_active_power"].shift(-HORIZON_MINUTES)
    X = df.drop(columns=["Global_active_power"])

    # Drop last rows where future target is not available
    valid = y.notna()
    X_h = X.loc[valid]
    y_h = y.loc[valid]

    print(f"✅ Prepared X/y: X={X_h.shape}, y={y_h.shape}")

    # ---- TIME-BASED TRAIN/VALIDATION SPLIT ----
    split_idx = int(len(X_h) * TRAIN_FRACTION)

    X_train, X_val = X_h.iloc[:split_idx], X_h.iloc[split_idx:]
    y_train, y_val = y_h.iloc[:split_idx], y_h.iloc[split_idx:]

    print(f"✅ Train: {X_train.shape}, Val: {X_val.shape}")
    if VERBOSE:
        print("Train period:", X_train.index.min(), "→", X_train.index.max())
        print("Val period:", X_val.index.min(), "→", X_val.index.max())

    # ---- SAMPLE TRAINING DATA FOR HEAVY MODELS ----
    if 0 < TRAIN_SAMPLE_FRAC < 1.0:
        train_sample_n = max(1, int(len(X_train) * TRAIN_SAMPLE_FRAC))
        sample_idx = X_train.sample(n=train_sample_n, random_state=RANDOM_STATE).index
        X_train_s = X_train.loc[sample_idx]
        y_train_s = y_train.loc[sample_idx]
        if VERBOSE:
            print(f"✅ Sampled train set for heavy models: {X_train_s.shape}")
    else:
        X_train_s, y_train_s = X_train, y_train

    # ---- BASELINE 1: PERSISTENCE ----
    # Predict y(t+H) using value at time t.
    # For y = shift(-H), aligned predictor is current Global_active_power at the same timestamps as y_h.
    persistence_series = df["Global_active_power"].iloc[:len(y_h)].copy()
    persistence_series.index = y_h.index

    persistence_pred_val = persistence_series.loc[y_val.index].to_numpy()
    all_results.append(evaluate_regression("baseline_persistence", HORIZON_MINUTES, y_val, persistence_pred_val))

    # ---- BASELINE 2: MEAN ----
    dummy = DummyRegressor(strategy="mean")
    dummy.fit(X_train, y_train)
    dummy_pred = dummy.predict(X_val)
    all_results.append(evaluate_regression("baseline_mean", HORIZON_MINUTES, y_val, dummy_pred))

    # ---- MODEL 1: LINEAR REGRESSION (SCALED) ----
    lin_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ])
    lin_pipe.fit(X_train, y_train)
    lin_pred = lin_pipe.predict(X_val)
    all_results.append(evaluate_regression("linear_regression_scaled", HORIZON_MINUTES, y_val, lin_pred))

    # ---- MODEL 2: RANDOM FOREST ----
    if RF_ENABLED:
        rf = RandomForestRegressor(
            n_estimators=200,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            max_depth=None,
            min_samples_leaf=2
        )
        rf.fit(X_train_s, y_train_s)
        rf_pred = rf.predict(X_val)
        all_results.append(evaluate_regression("random_forest", HORIZON_MINUTES, y_val, rf_pred))

    # ---- PRINT QUICK SUMMARY FOR THIS HORIZON ----
    horizon_df = pd.DataFrame([r for r in all_results if r["horizon_minutes"] == HORIZON_MINUTES]).sort_values("rmse")
    print("\n✅ Horizon performance (sorted by RMSE):")
    print(horizon_df)

# %%
# ---- SAVE ALL METRICS ----
metrics_df = pd.DataFrame(all_results).sort_values(["horizon_minutes", "rmse"])
print("\n✅ All results (sorted by horizon, then RMSE):")
print(metrics_df)

metrics_df.to_csv(METRICS_PATH, index=False)
print(f"\n✅ Saved metrics to: {METRICS_PATH}")