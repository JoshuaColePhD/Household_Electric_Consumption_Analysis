"""
04_evaluation.py

Purpose
-------
Summarize and visualize model performance results produced by `03_modeling.py`
across multiple forecast horizons.

This script:
- Loads model metrics from `data/model_metrics_by_horizon.csv`
- Ranks models within each horizon by RMSE and MAE
- Produces a compact summary table identifying the best-performing model(s) per horizon
- Creates horizon-aware comparison plots

Inputs
------
- data/model_metrics_by_horizon.csv

Outputs
-------
- data/evaluation_summary_by_horizon.csv
- figures/rmse_by_horizon.png
- figures/model_rmse_comparison_h15.png (example single-horizon bar chart)
"""

# %%
# ---- LIBRARY IMPORTS ----
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# %%
# ---- CONFIG ----
VERBOSE = True
SAVE_PLOTS = True
BAR_CHART_HORIZON = 15 

# %%
# ---- PATHS ----
DATA_DIR = Path("data")
FIGURES_DIR = Path("figures")

METRICS_PATH = DATA_DIR / "model_metrics_by_horizon.csv"
SUMMARY_PATH = DATA_DIR / "evaluation_summary_by_horizon.csv"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# %%
# ---- LOAD METRICS ----
metrics = pd.read_csv(METRICS_PATH)

required_cols = {"horizon_minutes", "model", "mae", "rmse", "r2"}
missing = required_cols - set(metrics.columns)
if missing:
    raise KeyError(f"Missing required columns in {METRICS_PATH.name}: {missing}")

print(f"✅ Loaded metrics: {metrics.shape}")
if VERBOSE:
    print("Horizons found:", sorted(metrics["horizon_minutes"].unique().tolist()))
    print(metrics.head())

# %%
# ---- RANK MODELS WITHIN EACH HORIZON ----
def rank_within_horizon(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    return (
        df.sort_values(["horizon_minutes", metric], ascending=[True, True])
          .groupby("horizon_minutes", as_index=False)
          .apply(lambda g: g.reset_index(drop=True))
          .reset_index(drop=True)
    )

# Print rankings
if VERBOSE:
    for h in sorted(metrics["horizon_minutes"].unique()):
        subset = metrics[metrics["horizon_minutes"] == h].sort_values("rmse")
        print(f"\n🏁 Horizon {h} min — ranking by RMSE (lower is better):")
        print(subset)

        subset = metrics[metrics["horizon_minutes"] == h].sort_values("mae")
        print(f"\n🏁 Horizon {h} min — ranking by MAE (lower is better):")
        print(subset)

# %%
# ---- SUMMARY TABLE: BEST MODEL PER HORIZON (RMSE + MAE) ----
best_by_rmse = (
    metrics.sort_values(["horizon_minutes", "rmse"])
           .groupby("horizon_minutes", as_index=False)
           .first()
           .assign(best_by="rmse")
)

best_by_mae = (
    metrics.sort_values(["horizon_minutes", "mae"])
           .groupby("horizon_minutes", as_index=False)
           .first()
           .assign(best_by="mae")
)

summary = pd.concat([best_by_rmse, best_by_mae], ignore_index=True)
summary = summary[["horizon_minutes", "best_by", "model", "mae", "rmse", "r2"]].sort_values(
    ["horizon_minutes", "best_by"]
)

summary.to_csv(SUMMARY_PATH, index=False)
print(f"\n✅ Saved evaluation summary to: {SUMMARY_PATH}")

# %%
# ---- PLOT 1: RMSE VS FORECAST HORIZON (SUMMARY PLOT) ----
if SAVE_PLOTS:
    plt.figure(figsize=(8, 5))

    for model_name in sorted(metrics["model"].unique()):
        model_df = metrics[metrics["model"] == model_name].sort_values("horizon_minutes")
        plt.plot(
            model_df["horizon_minutes"],
            model_df["rmse"],
            marker="o",
            label=model_name
        )

    plt.title("RMSE vs Forecast Horizon by Model")
    plt.xlabel("Forecast Horizon (minutes)")
    plt.ylabel("RMSE")
    plt.legend(title="Model")
    plt.grid(True)

    fig_path = FIGURES_DIR / "rmse_by_horizon.png"
    plt.savefig(fig_path, bbox_inches="tight")
    plt.show()

    print(f"📈 Saved horizon comparison plot to: {fig_path}")

# %%
# ---- PLOT 2: SINGLE-HORIZON RMSE BAR CHART ----
# This avoids confusing “global” ranking across different horizons.
if SAVE_PLOTS:
    if BAR_CHART_HORIZON not in metrics["horizon_minutes"].unique():
        print(f"⚠️ Horizon {BAR_CHART_HORIZON} not found; skipping bar chart.")
    else:
        plot_df = metrics[metrics["horizon_minutes"] == BAR_CHART_HORIZON].sort_values("rmse")

        plt.figure(figsize=(10, 4))
        plt.bar(plot_df["model"], plot_df["rmse"])
        plt.title(f"Model Comparison (RMSE) — Horizon = {BAR_CHART_HORIZON} min")
        plt.xlabel("Model")
        plt.ylabel("RMSE")
        plt.xticks(rotation=20, ha="right")

        fig_path = FIGURES_DIR / f"model_rmse_comparison_h{BAR_CHART_HORIZON}.png"
        plt.savefig(fig_path, bbox_inches="tight")
        plt.show()

        print(f"📈 Saved plot to: {fig_path}")

# %%
# ---- QUICK INTERPRETATION ----
if VERBOSE:
    print("\n📌 Best models per horizon:")
    for h in sorted(metrics["horizon_minutes"].unique()):
        best_rmse = metrics[metrics["horizon_minutes"] == h].sort_values("rmse").iloc[0]
        best_mae = metrics[metrics["horizon_minutes"] == h].sort_values("mae").iloc[0]
        print(
            f"- Horizon {h} min | Best RMSE: {best_rmse['model']} "
            f"(RMSE={best_rmse['rmse']:.4f}, MAE={best_rmse['mae']:.4f}, R²={best_rmse['r2']:.4f})"
        )
        print(
            f"              | Best MAE:  {best_mae['model']} "
            f"(MAE={best_mae['mae']:.4f}, RMSE={best_mae['rmse']:.4f}, R²={best_mae['r2']:.4f})"
        )