# Household Electricity Consumption Forecasting

A portfolio-ready time-series forecasting project that combines a reproducible Python analytics pipeline with an interactive dashboard designed for recruiter review and Vercel deployment.

**Analysis stack:** Python · pandas · scikit-learn · matplotlib · seaborn  
**Dashboard stack:** HTML · CSS · JavaScript · interactive SVG charts · static artifacts  
**Deployment target:** Vercel

---

## Live Dashboard

**Dashboard:** [https://householdelectricconsumptionanalysi.vercel.app](https://householdelectricconsumptionanalysi.vercel.app)  
**Source:** [GitHub repository](https://github.com/JoshuaColePhD/Household_Electric_Consumption_Analysis)

The dashboard is designed to make the modeling results explorable rather than buried in static tables. Recruiters and hiring managers will be able to compare model performance across forecast horizons, inspect how error changes over time, explore time-of-day consumption patterns, and review the modeling workflow at a glance.

The live dashboard is deployed on Vercel and optimized for fast public portfolio review.

---

## Key Results at a Glance

- **Dataset:** UCI Individual Household Electric Power Consumption
- **Observations:** ~2.0 million minute-level measurements
- **Forecast horizons:** 1, 15, and 60 minutes
- **Best-performing model by RMSE:** Random Forest Regressor
- **Validation approach:** time-aware train/validation split to avoid leakage
- **Main insight:** persistence is highly competitive at 1 minute, but degrades quickly as the forecast horizon increases; feature-based nonlinear models retain more predictive power at 15 and 60 minutes.

### Model Performance by Forecast Horizon

| Horizon | Persistence RMSE | Linear Regression RMSE | Random Forest RMSE |
|-------:|-----------------:|-----------------------:|-------------------:|
| 1 min  | 0.22 | 0.22 | **0.21** |
| 15 min | 0.70 | 0.60 | **0.56** |
| 60 min | 0.95 | 0.78 | **0.73** |

![RMSE vs Forecast Horizon](figures/rmse_by_horizon.png)

---

## Interactive Dashboard Features

The dashboard turns the project into a polished, recruiter-friendly product surface:

- **Horizon selector:** compare 1-, 15-, and 60-minute forecasting behavior.
- **Model comparison charts:** evaluate persistence, mean baseline, linear regression, and random forest results.
- **RMSE degradation view:** show how forecast error increases as prediction windows get longer.
- **Scenario explorer:** adjust horizon, model, time of day, and usage scenario to see how expected error and interpretation change.
- **Time-of-day usage patterns:** highlight daily household electricity rhythms.
- **Outlier-by-hour module:** show when unusually high consumption events cluster.
- **Methodology strip:** summarize the full pipeline from raw data to evaluation artifacts.

The dashboard is deployed as a static Vercel app using lightweight committed artifacts, not the full raw dataset.

---

## Data and Methodology

### Data Source

This project uses the **Individual Household Electric Power Consumption** dataset from the UCI Machine Learning Repository. The unit of analysis is minute-level household electricity measurement.

Key variables include:

- Global active power in kilowatts
- Global reactive power
- Voltage
- Global intensity
- Appliance-level sub-metering
- Timestamp at minute resolution

### Project Questions

- How predictable is household electricity usage at short and medium horizons?
- When are simple baselines sufficient, and when does machine learning add value?
- How quickly does forecast accuracy degrade as the prediction horizon increases?
- Which temporal features help capture household consumption dynamics?

### Workflow

1. **Load and clean:** fetch raw UCI data, validate schema, parse timestamps, normalize types, handle missing values, and flag outliers.
2. **Explore:** inspect daily, weekly, hourly, and outlier patterns to understand temporal structure.
3. **Engineer features:** create time-based, lag, rolling-window, and outlier-context features.
4. **Model:** evaluate persistence, mean baseline, scaled linear regression, and random forest models.
5. **Evaluate:** compare MAE, RMSE, and R² across 1-, 15-, and 60-minute horizons.
6. **Productize:** serve lightweight dashboard artifacts through an interactive Vercel app.

---

## Key Visual Findings

Household electricity consumption shows strong daily structure, with usage lowest overnight and higher during active household hours.

![Average Global Active Power by Hour](figures/avg_global_active_power_by_hour.png)

Outliers are retained and flagged rather than removed because they often represent meaningful household behavior such as appliance usage, heating, cooking, or other high-demand events.

![Outlier Frequency by Hour](figures/outlier_frequency_by_hour.png)

---

## Project Structure

```text
HOUSEHOLD_ELECTRIC_CONSUMPTION_ANALYSIS/
├── assets/
│   ├── dashboard.js                   # interactive dashboard behavior
│   └── styles.css                     # dashboard visual system
├── data/
│   ├── model_metrics_by_horizon.csv
│   ├── evaluation_summary_by_horizon.csv
│   └── *.csv                          # small committed result artifacts
├── figures/
│   ├── avg_global_active_power_by_hour.png
│   ├── daily_avg_global_active_power.png
│   ├── weekly_avg_global_active_power.png
│   ├── outlier_frequency_by_hour.png
│   ├── model_rmse_comparison_h15.png
│   └── rmse_by_horizon.png
├── src/
│   ├── 00_load_and_clean.py
│   ├── 01_eda.py
│   ├── 02_features.py
│   ├── 03_modeling.py
│   └── 04_evaluation.py
├── index.html                         # static dashboard entrypoint
├── package.json                       # Vercel build script
├── requirements.txt
├── vercel.json                        # Vercel static output configuration
└── README.md
```

Large raw and intermediate datasets are intentionally excluded from git. The analysis pipeline regenerates them locally, while the deployed dashboard consumes small committed summary artifacts.

---

## Run Locally

### 1. Reproduce the Python Analysis

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the pipeline from the project root:

```bash
python src/00_load_and_clean.py
python src/01_eda.py
python src/02_features.py
python src/03_modeling.py
python src/04_evaluation.py
```

### 2. Run the Dashboard

Build the static dashboard:

```bash
npm run build
```

Preview the built site locally:

```bash
cd dist
python3 -m http.server 5173
```

---

## Vercel Deployment

The dashboard is a static app deployed through Vercel.

- Vercel runs `npm run build`.
- The production output is served from `dist/`.
- The app will use lightweight exported CSV/JSON artifacts instead of raw household-level data.
- Raw UCI data, processed feature datasets, virtual environments, generated documentation, and local build artifacts remain excluded through `.gitignore`.

This keeps the deployed site fast, reproducible, and appropriate for a public portfolio repository.

---

## Skills Demonstrated

- Time-series data cleaning and validation
- Missing-value handling and outlier flagging
- Exploratory time-series analysis
- Feature engineering with lags, rolling statistics, and temporal indicators
- Baseline-aware forecasting
- Leakage-free model evaluation
- Multi-horizon performance comparison
- Communicating model results through a productized analytics dashboard
- Preparing an analytics project for frontend deployment and recruiter review

---

## Optional Extensions

- Incorporate weather or calendar features as exogenous predictors.
- Add longer-horizon or aggregated daily forecasting.
- Compare sequence-based models such as LSTM or temporal CNN architectures.
- Add richer scenario-based demand risk analysis to the dashboard.

---

## Contact

**Joshua Cole, PhD**  
Data Analytics · Time Series · Applied Modeling  
GitHub: [JoshuaColePhD](https://github.com/JoshuaColePhD)
