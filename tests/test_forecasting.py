"""Tests for time-aware validation, baselines, and metrics in src/forecasting.py."""

import numpy as np
import pandas as pd
import pytest

from forecasting import (
    TARGET,
    detect_outliers_iqr,
    evaluate_regression,
    make_horizon_target,
    mean_baseline,
    persistence_baseline,
    time_split,
)


@pytest.fixture
def minute_frame() -> pd.DataFrame:
    index = pd.date_range("2007-01-01", periods=100, freq="min", name="datetime")
    power = np.arange(100, dtype=float)
    return pd.DataFrame(
        {TARGET: power, "hour": index.hour, "lag_1": np.r_[np.nan, power[:-1]]},
        index=index,
    ).fillna(0.0)


# ---- target construction ----

def test_horizon_target_is_future_value(minute_frame):
    _, y = make_horizon_target(minute_frame, horizon=15)
    assert y.iloc[0] == minute_frame[TARGET].iloc[15]
    assert (y.to_numpy() == minute_frame[TARGET].to_numpy()[15:]).all()


def test_horizon_target_drops_current_target_and_trailing_rows(minute_frame):
    X, y = make_horizon_target(minute_frame, horizon=15)
    assert TARGET not in X.columns
    assert len(X) == len(y) == len(minute_frame) - 15
    assert X.index.equals(y.index)
    assert y.notna().all()


# ---- time-aware validation ----

def test_time_split_is_chronological_with_no_overlap(minute_frame):
    X, y = make_horizon_target(minute_frame, horizon=1)
    X_train, X_val, y_train, y_val = time_split(X, y, 0.8)
    assert X_train.index.max() < X_val.index.min()
    assert len(X_train) == int(len(X) * 0.8)
    assert len(X_train) + len(X_val) == len(X)
    assert X_train.index.intersection(X_val.index).empty
    assert y_train.index.equals(X_train.index) and y_val.index.equals(X_val.index)


def test_time_split_does_not_shuffle(minute_frame):
    X, y = make_horizon_target(minute_frame, horizon=1)
    X_train, X_val, _, _ = time_split(X, y, 0.5)
    assert X_train.index.is_monotonic_increasing
    assert X_val.index.is_monotonic_increasing


@pytest.mark.parametrize("fraction", [0, 1, -0.2, 1.5])
def test_time_split_rejects_invalid_fraction(minute_frame, fraction):
    X, y = make_horizon_target(minute_frame, horizon=1)
    with pytest.raises(ValueError):
        time_split(X, y, fraction)


# ---- baselines ----

def test_persistence_predicts_value_at_time_t(minute_frame):
    horizon = 15
    X, y = make_horizon_target(minute_frame, horizon)
    _, _, _, y_val = time_split(X, y, 0.8)
    pred = persistence_baseline(minute_frame, y, y_val)
    expected = minute_frame[TARGET].loc[y_val.index].to_numpy()
    np.testing.assert_array_equal(pred, expected)
    # On a linear ramp, persistence is off by exactly the horizon.
    np.testing.assert_allclose(y_val.to_numpy() - pred, horizon)


def test_mean_baseline_uses_training_mean_only(minute_frame):
    X, y = make_horizon_target(minute_frame, horizon=1)
    X_train, X_val, y_train, _ = time_split(X, y, 0.8)
    pred = mean_baseline(X_train, y_train, X_val)
    assert pred.shape == (len(X_val),)
    np.testing.assert_allclose(pred, y_train.mean())
    assert not np.isclose(pred[0], y.mean())  # validation data does not leak in


# ---- metrics ----

def test_evaluate_regression_known_values():
    y_true = pd.Series([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.0, 2.0, 3.0, 6.0])
    result = evaluate_regression("demo", 15, y_true, y_pred)
    assert result["horizon_minutes"] == 15 and result["model"] == "demo"
    assert result["mae"] == pytest.approx(0.5)
    assert result["rmse"] == pytest.approx(1.0)
    assert result["r2"] == pytest.approx(1 - 4 / 5)


def test_perfect_prediction_scores():
    y = pd.Series([0.5, 1.5, 2.5])
    result = evaluate_regression("perfect", 1, y, y.to_numpy())
    assert result["mae"] == 0 and result["rmse"] == 0 and result["r2"] == 1


# ---- cleaning ----

def test_iqr_outliers_flag_only_extremes():
    series = pd.Series([1.0, 1.1, 0.9, 1.0, 1.05, 50.0, -40.0])
    flags = detect_outliers_iqr(series)
    assert flags.tolist() == [False, False, False, False, False, True, True]
