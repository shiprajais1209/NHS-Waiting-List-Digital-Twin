import streamlit as st
import pandas as pd
import numpy as np
import joblib
from textwrap import dedent

severity_model = joblib.load(
    "Models/severity_18plus_linear_regression.joblib"
)

st.set_page_config(
    page_title="NHS Waiting List Digital Twin",
    page_icon="🏥",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Main app background */
    .stApp {
        background:
            linear-gradient(
                rgba(5, 20, 38, 0.92),
                rgba(5, 20, 38, 0.96)
            ),
            url("https://images.unsplash.com/photo-1587351021759-3e566b6af7cc");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Main content spacing */
    .block-container {
    padding-top: 4rem;
    padding-bottom: 3rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    max-width: 1400px;

    background: rgba(5, 18, 32, 0.78);
    border: 1px solid rgba(120, 180, 255, 0.12);
    border-radius: 24px;

    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.30);
    backdrop-filter: blur(8px);
}

    /* Titles */
    h1, h2, h3, h4 {
        color: #f4f8ff !important;
    }

    /* Normal text */
    p, label, span {
        color: #d7e4f2;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(15, 42, 68, 0.78);
        border: 1px solid rgba(120, 180, 255, 0.18);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.22);
        backdrop-filter: blur(10px);
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    /* Select box */
    div[data-baseweb="select"] > div {
        background: rgba(18, 45, 72, 0.9);
        border-radius: 10px;
    }

    /* Sliders */
    div[data-testid="stSlider"] {
        background: rgba(15, 42, 68, 0.55);
        padding: 14px;
        border-radius: 14px;
    }

    /* Info / warning boxes */
    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* KPI card hover effect */
div[data-testid="stMetric"] {
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 28px rgba(70, 160, 255, 0.18);
}

    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.12);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<div class="hero-section" style="
background:
linear-gradient(
    90deg,
    rgba(5, 28, 50, 0.96),
    rgba(5, 28, 50, 0.72)
),
url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d');
background-size: cover;
background-position: center;
padding: 32px;
border-radius: 20px;
margin-bottom: 26px;
">
<div class="hero-badge">DATA SCIENCE PORTFOLIO PROJECT</div>
<h1>Waiting List Digital Twin</h1>
<p class="hero-subtitle">NHS England RTT Waiting Times Analysis, Forecasting & Scenario Simulation</p>
<div class="hero-details">
<span>📅 April 2025 – June 2026</span>
<span>📊 Provider-Level Analytics</span>
<span>🔮 Forecasting & Simulation</span>
</div>
</div>
""", unsafe_allow_html=True)

baseline = pd.read_csv(
    "Outputs/june_2026_provider_baseline.csv"
)
provider_names = sorted(
    baseline["Provider Org Name"].unique()
)

selected_provider = st.selectbox(
    "Select NHS Provider",
    provider_names
)
selected_data = baseline[
    baseline["Provider Org Name"] == selected_provider
].iloc[0]

st.subheader(selected_provider)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Current Backlog",
        f"{selected_data['Total All']:,.0f}"
    )

with col2:
    st.metric(
        "New RTT Periods",
        f"{selected_data['New_RTT_Periods']:,.0f}"
    )

with col3:
    st.metric(
        "Completed RTT Pathways",
        f"{selected_data['Completed_RTT_Pathways']:,.0f}"
    )

historical = pd.read_csv(
    "Outputs/provider_historical_severity.csv"
)

historical["Date"] = pd.to_datetime(
    historical["Date"]
)
provider_history = historical[
    historical["Provider Org Name"] == selected_provider
].sort_values("Date")

st.subheader("Historical Waiting List Trend")

st.line_chart(
    provider_history.set_index("Date")["Total All"]
)
st.markdown(
    """
    <div style="
        background:
            linear-gradient(90deg, rgba(5,28,50,0.95), rgba(5,28,50,0.55)),
            url('https://images.unsplash.com/photo-1551076805-e1869033e561');
        background-size: cover;
        background-position: center;
        padding: 35px;
        border-radius: 20px;
        margin: 25px 0 20px 0;
        border: 1px solid rgba(120,180,255,0.15);
    ">
        <h2 style="margin:0;">Scenario Simulator</h2>
        <p style="margin-top:8px; margin-bottom:0;">
            Explore how changes in treatment capacity and RTT demand could affect waiting-list pressure.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

capacity_change = st.slider(
    "Change in Treatment Completion Capacity (%)",
    min_value=-20,
    max_value=30,
    value=10,
    step=1
)
demand_change = st.slider(
    "Change in New RTT Demand (%)",
    min_value=-20,
    max_value=30,
    value=0,
    step=1
)
completion_change = (
    selected_data["Completed_RTT_Pathways"]
    * (capacity_change / 100)
)

new_demand_change = (
    selected_data["New_RTT_Periods"]
    * (demand_change / 100)
)

scenario_backlog = (
    selected_data["Total All"]
    + new_demand_change
    - completion_change
)

scenario_backlog = max(
    0,
    scenario_backlog
)

backlog_difference = (
    scenario_backlog
    - selected_data["Total All"]
)

print_backlog = round(scenario_backlog)
print_difference = round(backlog_difference)

scenario_col1, scenario_col2 = st.columns(2)

with scenario_col1:
    st.metric(
        "Simulated Backlog",
        f"{print_backlog:,.0f}",
        delta=f"{print_difference:+,.0f} vs baseline",
        delta_color="inverse"
    )

with scenario_col2:
    percentage_change = (
        backlog_difference
        / selected_data["Total All"]
    ) * 100

    st.metric(
        "Backlog Change",
        f"{percentage_change:+.2f}%",
        delta=f"{print_difference:+,.0f} pathways",
        delta_color="inverse"
    )

break_even_data = pd.read_csv(
    "Outputs/june_2026_break_even_demand.csv"
)

selected_break_even = break_even_data[
    break_even_data["Provider Org Code"]
    == selected_data["Provider Org Code"]
]

if not selected_break_even.empty:
    break_even_pct = selected_break_even[
        "Break_Even_Demand_Increase_Pct"
    ].iloc[0]
else:
    break_even_pct = np.nan

st.subheader("Scenario Resilience")

if not np.isnan(break_even_pct):
    st.metric(
        "Break-even Demand Increase",
        f"{((selected_data['Completed_RTT_Pathways'] * (capacity_change / 100)) / selected_data['New_RTT_Periods'] * 100):.2f}%"
    )

    st.caption(
    "Estimated demand increase that would offset the backlog benefit "
    "of the selected treatment completion capacity change."
)
    st.info(
    "Simulation note: This is an assumption-based counterfactual scenario model. "
    "It estimates the effect of changes in RTT demand and treatment completion "
    "capacity while holding other factors constant. Actual waiting-list changes "
    "may also reflect RTT clock adjustments, patient transfers, data revisions "
    "and other operational factors."
)
st.divider()

st.header("18+ Week Waiting Pressure")

st.caption(
    "Monitoring the percentage of incomplete RTT pathways "
    "waiting more than 18 weeks."
)
severity_data = pd.read_csv(
    "Outputs/provider_historical_severity.csv"
)

severity_data["Date"] = pd.to_datetime(severity_data["Date"])

selected_severity = severity_data[
    severity_data["Provider Org Code"]
    == selected_data["Provider Org Code"]
].copy()

selected_severity = selected_severity.sort_values("Date")

severity_chart = selected_severity.set_index("Date")[
    ["Pct_18_Plus"]
]

st.line_chart(severity_chart)

latest_severity = selected_severity.iloc[-1]

st.metric(
    "Current 18+ Week Waiting Pressure",
    f"{latest_severity['Pct_18_Plus']:.2f}%"
)

st.subheader("Long-Wait Severity")

sev_col1, sev_col2, sev_col3 = st.columns(3)

with sev_col1:
    st.metric(
        "52+ Weeks",
        f"{latest_severity['Pct_52_Plus']:.2f}%"
    )

with sev_col2:
    st.metric(
        "65+ Weeks",
        f"{latest_severity['Pct_65_Plus']:.2f}%"
    )

with sev_col3:
    st.metric(
        "104+ Weeks",
        f"{latest_severity['Pct_104_Plus']:.2f}%"
    )

latest_four = selected_severity.tail(4).copy()

current_pct = latest_four["Pct_18_Plus"].iloc[-1]
lag_1 = latest_four["Pct_18_Plus"].iloc[-2]
lag_2 = latest_four["Pct_18_Plus"].iloc[-3]
lag_3 = latest_four["Pct_18_Plus"].iloc[-4]

prediction_features = pd.DataFrame(
    [[current_pct, lag_1, lag_2, lag_3]],
    columns=[
        "Pct_18_Plus",
        "Pct_18_Lag_1",
        "Pct_18_Lag_2",
        "Pct_18_Lag_3"
    ]
)

predicted_18_plus = severity_model.predict(
    prediction_features
)[0]

st.markdown(
    """
    <div style="
        background:
            linear-gradient(90deg, rgba(5,28,50,0.96), rgba(5,28,50,0.58)),
            url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d');
        background-size: cover;
        background-position: center;
        padding: 35px;
        border-radius: 20px;
        margin: 25px 0 20px 0;
        border: 1px solid rgba(120,180,255,0.15);
    ">
        <h2 style="margin:0;">Next-Month 18+ Pressure Forecast</h2>
        <p style="margin-top:8px; margin-bottom:0;">
            Forecasting next month's provider-level 18+ week waiting pressure using historical RTT trends.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.metric(
    "Predicted 18+ Waiting Pressure",
    f"{predicted_18_plus:.2f}%"
)

forecast_change = predicted_18_plus - current_pct

st.metric(
    "Forecasted Change",
    f"{forecast_change:+.2f} percentage points",
    delta="vs current month",
    delta_color="off"
)

high_pressure_threshold = 37.1943

if predicted_18_plus >= high_pressure_threshold:
    st.error(
        f"⚠️ HIGH PRESSURE WARNING — Forecast exceeds the "
        f"{high_pressure_threshold:.2f}% project threshold."
    )
else:
    st.success(
        f"✓ Below High-Pressure Threshold ({high_pressure_threshold:.2f}%)"
    )

st.caption(
    "High-pressure threshold: 37.19%. "
    "This is a project-specific, data-driven threshold defined as the "
    "75th percentile of next-month 18+ waiting pressure in the training data. "
    "It is not an official NHS performance target."
)

st.markdown("#### Forecast Model Performance")

m1, m2, m3 = st.columns(3)

m1.metric("Test MAE", "2.06 pp")
m2.metric("Test RMSE", "3.46 pp")
m3.metric("Test R²", "0.9368")

st.caption(
    "Linear Regression evaluated on a chronological held-out test period "
    "(April–May 2026). Performance is reported against actual next-month "
    "18+ week waiting pressure."
)

st.markdown("#### Model vs Persistence Baseline")

comparison_data = pd.DataFrame({
    "Model": ["Persistence Baseline", "Linear Regression"],
    "MAE (pp)": [2.10, 2.06],
    "RMSE (pp)": [3.60, 3.46],
    "R²": [0.9318, 0.9368]
})

st.dataframe(
    comparison_data,
    hide_index=True,
    use_container_width=True
)

st.caption(
    "Linear Regression produced a modest improvement over the persistence "
    "baseline, where next month's 18+ waiting pressure is assumed to remain "
    "equal to the current month."
)

st.divider()

st.header("High-Pressure Early Warning")

st.write(
    "An additional classification model was evaluated to identify providers "
    "likely to enter the project's high-pressure category in the following month."
)

c1, c2, c3 = st.columns(3)

c1.metric("Precision", "83.96%")
c2.metric("Recall", "95.15%")
c3.metric("F1 Score", "89.20%")

st.caption(
    "Logistic Regression with standardized severity and RTT flow features, "
    "using a probability threshold of 0.75 selected on the training data. "
    "Results shown are from the chronological held-out test period."
)

st.markdown("#### Early-Warning Model vs Persistence Baseline")

classification_comparison = pd.DataFrame({
    "Method": ["Persistence Baseline", "Logistic Regression"],
    "Precision": ["84.86%", "83.96%"],
    "Recall": ["95.15%", "95.15%"],
    "F1 Score": ["89.71%", "89.20%"]
})

st.dataframe(
    classification_comparison,
    hide_index=True,
    use_container_width=True
)

st.caption(
    "The persistence baseline performed slightly better overall. "
    "The machine-learning classifier achieved the same recall and identified "
    "one high-pressure threshold crossing that the persistence rule missed, "
    "but it also produced slightly more false positives."
)

st.divider()

st.header("Model & Simulation Limitations")

st.info(
    """
    • The analysis uses 15 months of NHS RTT data (April 2025–June 2026), 
    so the available time-series history is relatively short.

    • Forecasts and early-warning predictions should be interpreted as 
    analytical estimates rather than operational NHS predictions.

    • The scenario simulator is assumption-based and does not establish 
    causal effects of capacity or demand changes.

    • Actual waiting-list movements can also be influenced by RTT clock 
    adjustments, patient transfers, reporting revisions and other 
    operational factors.
    """
)

st.divider()

st.header("Data Source")

st.write(
    "This project uses publicly available Referral to Treatment (RTT) "
    "waiting-times data published by NHS England."
)

st.markdown(
    "[View NHS England RTT Waiting Times Data]"
    "(https://www.england.nhs.uk/statistics/statistical-work-areas/"
    "rtt-waiting-times/)"
)

st.caption(
    "Data period used in this project: April 2025–June 2026. "
    "This is an independent portfolio project and is not affiliated with "
    "or endorsed by NHS England."
)

