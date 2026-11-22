"""Reusable forecasting helpers shared by the pipeline scripts and the test suite.

The numbered scripts in ``src/`` run top to bottom, so the logic that the
results depend on (target construction, time-aware validation, baselines, and
metrics) lives here, where it can be tested without the full UCI dataset.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

TARGET = "Global_active_power"


def detect_outliers_iqr(series: pd.Series, factor: float = 1.5) -> pd.Series:
    """Flag values outside [Q1 - factor*IQR, Q3 + factor*IQR]."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    return (series < lower) | (series > upper)


def make_horizon_target(
    df: pd.DataFrame, horizon: int, target: str = TARGET
) -> tuple[pd.DataFrame, pd.Series]:
    """Return (X, y) where y is ``target`` ``horizon`` rows ahead.

    The current target column is dropped from X to avoid trivial leakage, and
    trailing rows without a future value are removed.
    """
    y = df[target].shift(-horizon)
    X = df.drop(columns=[target])
    valid = y.notna()
    return X.loc[valid], y.loc[valid]


def time_split(X: pd.DataFrame, y: pd.Series, train_fraction: float):
    """Chronological split: the first ``train_fraction`` of rows train, the rest validate."""
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1")
    split_idx = int(len(X) * train_fraction)
    return X.iloc[:split_idx], X.iloc[split_idx:], y.iloc[:split_idx], y.iloc[split_idx:]


def persistence_baseline(df: pd.DataFrame, y_h: pd.Series, y_val: pd.Series, target: str = TARGET) -> np.ndarray:
    """Predict y(t+H) with the observed value at time t, for the validation rows."""
    persistence = df[target].iloc[: len(y_h)].copy()
    persistence.index = y_h.index
    return persistence.loc[y_val.index].to_numpy()


def mean_baseline(X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame) -> np.ndarray:
    """Predict the training-set mean for every validation row."""
    dummy = DummyRegressor(strategy="mean")
    dummy.fit(X_train, y_train)
    return dummy.predict(X_val)


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

