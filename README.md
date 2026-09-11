# NHS Waiting List Digital Twin

A digital-twin-style analytics and scenario simulation project for exploring NHS Referral to Treatment (RTT) waiting-list pressure at provider level.

The project uses official NHS England RTT data to analyse historical waiting-list trends, forecast next-month 18+ week waiting pressure, identify providers at risk of high waiting pressure, and simulate how changes in treatment capacity and new RTT demand could affect future backlog levels.

## Live Demo

🔗 [Open the Streamlit Dashboard](https://nhs-waiting-list-digital-twin-shipra.streamlit.app)

## Project Overview

NHS waiting lists are influenced by changing patient demand, treatment capacity, long-waiting pathways, transfers, RTT clock adjustments, and other operational factors.

This project develops a data-driven decision-support prototype that combines:

- Historical NHS RTT waiting-list analysis
- Provider-level waiting-pressure monitoring
- Next-month 18+ week pressure forecasting
- High-pressure early-warning analytics
- Treatment-capacity and demand scenario simulation
- Interactive Streamlit dashboard

The project should be interpreted as a **digital-twin-style scenario simulator**, rather than an operational NHS digital twin or clinical decision-making system.

## Data

**Source:** NHS England Referral to Treatment (RTT) Waiting Times

**Period analysed:** April 2025 – June 2026

The analysis uses 15 monthly NHS England RTT full extracts.

Key RTT components used include:

- **Part 2:** Incomplete pathways / patients still waiting
- **Part 1A & Part 1B:** Completed RTT pathways
- **Part 3:** New RTT periods
- Weekly waiting-time bands for measuring 18+, 52+, 65+, and 104+ week waiting pressure

The raw NHS CSV extracts are not included in this repository because of their size. They can be downloaded from the official NHS England RTT statistics pages.

NHS England RTT data:
https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/

## Data Processing

The raw RTT extracts contain provider, commissioner, treatment-function and pathway-level records.

The processing pipeline:

1. Loads and combines monthly RTT extracts.
2. Filters incomplete RTT pathways for backlog analysis.
3. Removes treatment-function total rows (`C_999`) when aggregating specialties to avoid double counting.
4. Aggregates data to provider-month level.
5. Calculates long-wait measures including 18+, 52+, 65+, and 104+ weeks.
6. Combines waiting-list severity with new RTT periods and completed pathways.
7. Constructs lagged features for forecasting.

The final modelling panel contains **440 providers across 15 monthly periods** after data-quality filtering.

## Forecasting 18+ Week Waiting Pressure

The forecasting task predicts each provider's percentage of incomplete RTT pathways waiting more than 18 weeks in the following month.

A chronological train/test design was used to avoid randomly mixing future observations into the training data.

### Final Model

**Linear Regression**

| Metric | Linear Regression | Persistence Baseline |
|---|---:|---:|
| MAE | 2.06 percentage points | 2.10 percentage points |
| RMSE | 3.46 | 3.60 |
| R² | 0.9368 | 0.9318 |

Linear Regression produced a modest improvement over the persistence baseline.

Because the dataset contains a relatively short time dimension, these results should be interpreted as a proof-of-concept rather than evidence of long-term forecasting performance.

## High-Pressure Early Warning

A provider is classified as high pressure when its predicted 18+ week waiting percentage exceeds the project-specific threshold of:

**37.19%**

This threshold corresponds to the 75th percentile of the training data and is **not an official NHS performance threshold**.

The early-warning model was compared against a persistence baseline.

| Metric | Logistic Regression | Persistence Baseline |
|---|---:|---:|
| Accuracy | 95.68% | 95.91% |
| Precision | 83.96% | 84.86% |
| Recall | 95.15% | 95.15% |
| F1 Score | 89.20% | 89.71% |

The persistence baseline performed slightly better overall, highlighting the importance of benchmarking machine-learning models against simple operational baselines.

## Scenario Simulator

The Streamlit dashboard contains an assumption-based scenario simulator that allows users to change:

- Treatment completion capacity
- New RTT demand

The simulator estimates how these changes could affect the following month's waiting-list backlog.

A simplified scenario relationship is used:

**Next Backlog ≈ Current Backlog + New RTT Demand − Completed RTT Pathways**

The simulator holds other factors constant. Actual NHS waiting-list movements may also reflect RTT clock adjustments, patient transfers, data revisions, and other operational factors.

Therefore, scenario outputs should be interpreted as **counterfactual planning estimates rather than causal predictions**.

## Interactive Dashboard

The Streamlit application provides:

- NHS provider selection
- Current waiting-list metrics
- Historical backlog trends
- Interactive capacity and demand scenario controls
- Scenario resilience analysis
- 18+ week waiting-pressure trends
- Long-wait severity indicators
- Next-month waiting-pressure forecasts
- High-pressure early-warning indicators
- Model-versus-baseline performance comparisons

## Project Structure

```text
NHS-Waiting-List-Digital-Twin/
│
├── Models/
│   └── severity_18plus_linear_regression.joblib
│
├── Notebooks/
│   └── 01_data_exploration.ipynb
│
├── Outputs/
│   ├── june_2026_break_even_demand.csv
│   ├── june_2026_provider_baseline.csv
│   └── provider_historical_severity.csv
│
├── SRC/
│   └── app.py
│
├── .gitignore
├── requirements.txt
└── README.md

