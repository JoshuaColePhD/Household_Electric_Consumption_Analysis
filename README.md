# Household Electricity Consumption Forecasting  
**Tools:** Python · pandas · scikit-learn · matplotlib · seaborn  

---

## Overview

This project develops a reproducible, time-aware forecasting pipeline to model household electricity consumption using high-frequency (minute-level) power usage data. Rather than treating electricity demand as a static quantity, the analysis explicitly models **short- and medium-term temporal dynamics** and evaluates predictive performance across multiple forecast horizons.

The workflow progresses from robust data cleaning and exploratory time-series analysis to feature engineering, baseline modeling, and multi-horizon evaluation. Strong emphasis is placed on **baseline comparison, leakage-free validation, and honest interpretation of model performance**.

---

## Key Results at a Glance

- **Observations:** ~2.0 million minute-level measurements  
- **Forecast horizons evaluated:** 1, 15, and 60 minutes  
- **Best-performing model:** Random Forest Regressor  
- **Key insight:** As forecast horizon increases, naive persistence degrades rapidly while feature-based nonlinear models retain predictive power  

### Model Performance (RMSE)

| Horizon | Persistence | Linear Regression | Random Forest |
|-------:|------------:|------------------:|--------------:|
| 1 min  | 0.22 | 0.22 | **0.21** |
| 15 min | 0.70 | 0.60 | **0.56** |
| 60 min | 0.95 | 0.78 | **0.73** |

---

## Key Questions

- How predictable is household electricity usage at short vs. medium horizons?
- When do simple baselines suffice, and when does machine learning add value?
- How does forecast accuracy degrade as prediction horizons increase?
- What role do temporal features (lags, rolling statistics, time-of-day effects) play in forecasting performance?

---

## Data

**Source:**  
Individual Household Electric Power Consumption dataset (UCI Machine Learning Repository)

**Unit of analysis:**  
Minute-level household electricity measurements

**Key variables include:**
- Global active power (kW)
- Voltage and current intensity
- Appliance-level sub-metering
- Timestamp (minute resolution)

The dataset spans multiple years, enabling robust analysis of daily, weekly, and long-term consumption patterns.

---

## Project Structure
```
HOUSEHOLD_ELECTRIC_CONSUMPTION_ANALYSIS/
├── data/
│   ├── individual_household_electric_power_consumption.csv
│   ├── processed_power_data.csv
│   ├── feature_power_data.csv
│   ├── model_metrics.csv
│   ├── model_metrics_by_horizon.csv
│   ├── evaluation_summary.csv
│   └── evaluation_summary_by_horizon.csv
├── figures/
│   ├── avg_global_active_power_by_hour.png
│   ├── daily_avg_global_active_power.png
│   ├── weekly_avg_global_active_power.png
│   ├── outlier_frequency_by_hour.png
│   ├── model_rmse_comparison.png
│   ├── model_rmse_comparison_h15.png
│   └── rmse_by_horizon.png
├── src/
│   ├── 00_load_and_clean.py
│   ├── 01_eda.py
│   ├── 02_features.py
│   ├── 03_modeling.py
│   └── 04_evaluation.py
├── .gitignore
├── requirements.txt
└── README.md
```
---

## Methods

### 1️⃣ Data Loading & Cleaning (`00_load_and_clean.py`)

Raw data are preserved as a source of truth while producing a clean, analysis-ready dataset. Key steps include:

- Schema validation and defensive checks  
- Robust datetime parsing and indexing  
- Data type normalization  
- Explicit missing-value handling  
- Encoding of appliance-level missingness  
- Detection (but not removal) of outliers using global and time-aware criteria  

Outliers are retained and flagged rather than removed, as they represent meaningful household behavior rather than sensor noise.

**Output:**  
- `data/processed_power_data.csv`

---

### 2️⃣ Exploratory Data Analysis (`01_eda.py`)

EDA focuses on understanding temporal structure and variability prior to modeling.

Household electricity consumption exhibits strong diurnal patterns, with usage lowest overnight and peaking during morning and evening hours.

![Average Global Active Power by Hour](figures/avg_global_active_power_by_hour.png)

These patterns reflect typical household routines and motivate the inclusion of time-based features in modeling.

**Key findings:**
- Strong **diurnal consumption patterns** with evening peaks  
- Highly **right-skewed, multi-modal distributions**, indicating distinct operating states  
- Outliers are **rare but structured**, clustering in predictable time windows  
- Daily and weekly trends are stable, with short-term variability dominating  

These insights directly guide feature engineering and horizon selection.

---

### 3️⃣ Feature Engineering (`02_features.py`)

Temporal context is made explicit through engineered features:

- Time-based features (hour, day of week, weekend indicators)  
- Lagged consumption values  
- Rolling window statistics  
- Retention of outlier flags as contextual indicators  

Rows with missing values introduced by lag/rolling operations are dropped once at the end of feature creation.

**Output:**  
- `data/feature_power_data.csv`

---

### 4️⃣ Modeling (`03_modeling.py`)

The task is framed as a **time-series forecasting problem**, evaluated across multiple horizons (1, 15, 60 minutes).

**Modeling practices include:**
- Time-aware train/validation splits  
- Strong baselines (persistence, mean)  
- Feature scaling within pipelines to avoid leakage  
- Evaluation using MAE, RMSE, and R²  

**Models evaluated:**
- Persistence baseline  
- Mean baseline  
- Scaled linear regression  
- Random forest regression (sampled for efficiency)

---

### 5️⃣ Evaluation (`04_evaluation.py`)

Evaluation consolidates results across horizons and visualizes how forecast difficulty changes over time.

**Key evaluation insights:**
- Persistence is highly competitive at very short horizons due to strong temporal autocorrelation
- Machine learning models provide increasing gains at 15- and 60-minute horizons
- Random Forest models consistently achieve the lowest RMSE as horizon increases

![RMSE vs Forecast Horizon](figures/rmse_by_horizon.png)

*Forecast error increases with horizon for all models, while feature-based nonlinear models degrade more gracefully than naive baselines.*

**Outputs:**
- `data/model_metrics_by_horizon.csv`  
- `data/evaluation_summary_by_horizon.csv`  
- `figures/rmse_by_horizon.png`

---

## Why Multi-Horizon Forecasting?

Evaluating only a single horizon can be misleading. This project demonstrates that:

- **Short-horizon forecasting** is dominated by temporal autocorrelation  
- **Medium-horizon forecasting** benefits substantially from engineered features  
- **Longer horizons** require nonlinear models to retain predictive power  

This perspective aligns modeling complexity with business and operational needs.

---

## Reproducibility

All scripts use relative paths and can be run end-to-end from the project root:
```bash
python src/00_load_and_clean.py
python src/01_eda.py
python src/02_features.py
python src/03_modeling.py
python src/04_evaluation.py
```
All intermediate datasets and figures are generated deterministically from the raw data.

---

## Skills Demonstrated

- Time-series data cleaning and validation  
- Exploratory time-series analysis  
- Feature engineering for temporal models  
- Baseline-aware forecasting  
- Leakage-free model evaluation  
- Multi-horizon performance analysis  
- Reproducible analytics pipelines in Python  

---

## Next Steps (Optional Extensions)

- Incorporation of exogenous variables (e.g., weather)  
- Longer-horizon or aggregated forecasting  
- Sequence-based models (e.g., LSTM, temporal CNNs)  
- Scenario-based demand risk analysis  

---

## Contact

**Joshua Cole, PhD**  
Data Analytics · Time Series · Applied Modeling  
GitHub: https://github.com/JoshuaColePhD  