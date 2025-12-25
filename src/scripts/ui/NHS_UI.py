import math
import numbers
import os,sys
import textwrap
from typing import Optional, Tuple
import pandas as pd
import plotly.express as px
import streamlit as st

path = os.getcwd()
sys.path.append(path)
from src.scripts.ui.azureOpenAI_st import aiResp

st.set_page_config(layout='wide',
                   page_title='AI MedAssitant',
                   )

APP_STYLE = """
<style>
:root{
  --bg:#0b1220;
  --panel:#0f1a2e;
  --panel2:#111f38;
  --muted:#93a4c7;
  --text:#e8efff;
  --brand:#3b82f6;
  --good:#22c55e;
  --warn:#f59e0b;
  --bad:#ef4444;
  --border:rgba(255,255,255,.08);
  --shadow: 0 10px 25px rgba(0,0,0,.35);
  --radius: 16px;
  --radius2: 12px;
}
.stApp{
  background: radial-gradient(1200px 800px at 20% 0%, #12234a 0%, var(--bg) 50%, #070c16 100%);
  color:var(--text);
}
.block-container{
  padding-top:20px;
  padding-left:24px;
  padding-right:24px;
}
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
  border-right:1px solid var(--border);
}
section[data-testid="stSidebar"] .css-1d391kg{
  color:var(--text);
}
pre code, code {
  white-space: pre-wrap !important;
  word-break: break-word;
}
.hero{
  display:flex;
  gap:20px;
  align-items:stretch;
  background:linear-gradient(120deg, rgba(59,130,246,0.22), rgba(17,24,39,0.75));
  border:1px solid var(--border);
  box-shadow:var(--shadow);
  padding:18px 20px;
  border-radius:var(--radius);
}
.hero .eyebrow{
  letter-spacing:0.1em;
  text-transform:uppercase;
  color:var(--muted);
  font-size:0.75rem;
  margin:0 0 6px 0;
}
.hero h1{
  margin:0;
  font-size:1.6rem;
  color:var(--text);
}
.hero .subtitle{
  color:var(--muted);
  margin:6px 0 10px 0;
}
.hero .meta{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
}
.hero .stat-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:10px;
  min-width:260px;
}
.pill{
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding:6px 12px;
  border-radius:999px;
  font-weight:600;
  font-size:0.8rem;
  background:rgba(255,255,255,0.06);
  border:1px solid var(--border);
  color:var(--text);
}
.pill.good{ background:rgba(34,197,94,0.12); color:#6ee7b7; border-color:rgba(110,231,183,.4);}
.pill.warn{ background:rgba(245,158,11,0.12); color:#fbbf24; border-color:rgba(251,191,36,.35);}
.pill.bad{ background:rgba(239,68,68,0.12); color:#fca5a5; border-color:rgba(252,165,165,.35);}
.metric-card{
  background:var(--panel);
  border-radius:var(--radius2);
  padding:12px 14px;
  border:1px solid var(--border);
  box-shadow:var(--shadow);
  color:var(--text);
}
.metric-card h4{
  margin:0;
  font-size:0.85rem;
  color:var(--muted);
  letter-spacing:0.02em;
}
.metric-card p{
  margin:4px 0 2px 0;
  font-size:1.45rem;
  font-weight:700;
}
.badge{
  display:inline-flex;
  align-items:center;
  gap:6px;
  background:rgba(59,130,246,0.15);
  color:#9bc2ff;
  padding:4px 10px;
  border-radius:999px;
  font-size:0.75rem;
  font-weight:600;
}
.badge--warning { background: rgba(245,158,11,0.16); color: #facc15; }
.badge--danger { background: rgba(239,68,68,0.16); color: #fca5a5; }
.card-shell{
  background:var(--panel);
  border:1px solid var(--border);
  padding:14px 16px;
  border-radius:var(--radius);
  box-shadow:var(--shadow);
}
.title-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  margin-bottom:6px;
}
.title-row h3{ margin:0; color:var(--text); }
.title-row .muted{ color:var(--muted); }
.muted{ color:var(--muted); }
.stTabs [data-baseweb="tab"]{
  background:var(--panel2);
  color:var(--text);
  border:1px solid var(--border);
  border-bottom:none;
  margin-right:6px;
  border-radius:var(--radius2) var(--radius2) 0 0;
}
.stTabs [data-baseweb="tab"]:hover{
  background:rgba(255,255,255,0.04);
}
.stTabs [aria-selected="true"]{
  background:var(--panel);
  color:var(--text);
  border-bottom:1px solid var(--panel);
}
div[data-testid="stPlotlyChart"]{
  background:var(--panel);
  padding:12px;
  border-radius:var(--radius);
  border:1px solid var(--border);
  box-shadow:var(--shadow);
}
div[data-testid="stDataFrame"]{
  background:var(--panel);
  padding:8px;
  border-radius:var(--radius2);
  border:1px solid var(--border);
  box-shadow:var(--shadow);
}
[data-testid="stTable"] table{
  background:var(--panel);
  color:var(--text);
}
[data-testid="stMarkdown"] table{
  background:var(--panel);
  color:var(--text);
}
div[data-baseweb="select"]{
  color:var(--text);
}
/* tweak inputs */
input, textarea{
  background:var(--panel2) !important;
  color:var(--text) !important;
  border-radius:10px !important;
  border:1px solid var(--border) !important;
}
/* emphasis for alert blocks */
.callout{
  background:rgba(239,68,68,0.08);
  border:1px solid rgba(239,68,68,0.35);
  color:#fecaca;
  padding:10px 12px;
  border-radius:var(--radius2);
  margin-bottom:8px;
}
.callout.warn{
  background:rgba(245,158,11,0.08);
  border-color:rgba(245,158,11,0.35);
  color:#fcd34d;
}
.empty-state{
  background:var(--panel);
  border:1px dashed var(--border);
  padding:18px;
  border-radius:var(--radius);
  text-align:center;
  color:var(--muted);
}
</style>
"""

st.markdown(APP_STYLE, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_ai_response(patient_id: int):
    return aiResp(patient_id)

def color_habits(val):
    color = 'red' if val in ['Yes','Unhealthy'] else 'orange' if val=='Moderate' else 'green'
    return f'background-color: {color}'

def color_bmi(val):
    color = 'red' if val >29.9 else 'orange' if val>25 else 'green'
    return f'background-color: {color}'

def color_hist(val):
    color = 'red' if val=='Yes' else 'green'
    return f'background-color: {color}'

def color_bp(val):
    color = 'red' if val=='High' else 'green'
    return f'background-color: {color}'

def render_metric_card(title: str, value: str | int | float, badge: str | None = None, badge_level: str = "info"):
    badge_html = ""
    if badge:
        badge_class = "badge"
        if badge_level == "warning":
            badge_class += " badge--warning"
        elif badge_level == "danger":
            badge_class += " badge--danger"
        badge_html = f'<span class="{badge_class}">{badge}</span>'
    return textwrap.dedent(
        f"""
        <div class="metric-card">
            <h4>{title}</h4>
            <p>{value}</p>
            {badge_html}
        </div>
        """
    ).strip()

def render_kpi(title: str, value: str, delta: str | None = None, tone: str = "good") -> str:
    pill_class = "pill"
    if tone in {"good", "warn", "bad"}:
        pill_class += f" {tone}"
    delta_html = f'<span class="{pill_class}">{delta}</span>' if delta else ""
    return textwrap.dedent(
        f"""
        <div class="metric-card">
            <div class="title-row">
                <h4>{title}</h4>
                {delta_html}
            </div>
            <p>{value}</p>
        </div>
        """
    ).strip()

def score_vitals_risk(row: pd.Series, bmi_val: Optional[float]) -> list[dict]:
    """Return risk scores (0-100, higher = riskier) for radar plot."""
    scores = []
    # BP score
    try:
        sys_bp = float(row.get('Systolic BP(mmHg)', math.nan))
        dia_bp = float(row.get('Diastolic(mmHg)', math.nan))
    except (TypeError, ValueError):
        sys_bp = dia_bp = math.nan
    bp_score = None
    if not math.isnan(sys_bp) and not math.isnan(dia_bp):
        if sys_bp >= 160 or dia_bp >= 100:
            bp_score = 92
        elif sys_bp >= 140 or dia_bp >= 90:
            bp_score = 78
        elif sys_bp >= 130 or dia_bp >= 85:
            bp_score = 64
        elif sys_bp >= 120 or dia_bp >= 80:
            bp_score = 48
        else:
            bp_score = 28
    elif isinstance(row.get('Result_BP'), str):
        bp_score = 78 if row.get('Result_BP', '').lower() == 'high' else 42
    if bp_score is not None:
        scores.append({"Metric": "Blood Pressure", "Score": bp_score})

    # Cholesterol
    chol_score = None
    try:
        ldl_val = float(row.get('LDL (mg/dL)', math.nan))
    except (TypeError, ValueError):
        ldl_val = math.nan
    if not math.isnan(ldl_val):
        if ldl_val >= 160:
            chol_score = 92
        elif ldl_val >= 130:
            chol_score = 76
        elif ldl_val >= 100:
            chol_score = 62
        else:
            chol_score = 34
    elif isinstance(row.get('Result_cholesterol'), str):
        chol_score = 72 if row.get('Result_cholesterol', '').lower() == 'high' else 42
    if chol_score is not None:
        scores.append({"Metric": "Cholesterol", "Score": chol_score})

    # HbA1c
    hba1c_score = None
    try:
        hba1c_val = float(row.get('HbA1c', math.nan))
    except (TypeError, ValueError):
        hba1c_val = math.nan
    if not math.isnan(hba1c_val):
        if hba1c_val >= 9:
            hba1c_score = 96
        elif hba1c_val >= 8:
            hba1c_score = 82
        elif hba1c_val >= 7:
            hba1c_score = 70
        elif hba1c_val >= 6.5:
            hba1c_score = 58
        elif hba1c_val >= 6:
            hba1c_score = 44
        else:
            hba1c_score = 28
    if hba1c_score is not None:
        scores.append({"Metric": "HbA1c", "Score": hba1c_score})

    # BMI
    if bmi_val is not None and not math.isnan(bmi_val):
        if bmi_val >= 35:
            bmi_score = 95
        elif bmi_val >= 30:
            bmi_score = 82
        elif bmi_val >= 27.5:
            bmi_score = 72
        elif bmi_val >= 25:
            bmi_score = 60
        elif bmi_val >= 18.5:
            bmi_score = 32
        else:
            bmi_score = 54  # underweight risk
        scores.append({"Metric": "BMI", "Score": bmi_score})
    return scores

def lifestyle_scores(row: pd.Series) -> pd.DataFrame:
    """Create a simple lifestyle scoring table for visualisation."""
    mappings = {
        'Smoking': {'No': 10, 'Former': 25, 'Yes': 85},
        'Drinking': {'No': 12, 'Moderate': 36, 'Yes': 72, 'Heavy': 90},
        'Food habits': {'Healthy': 18, 'Moderate': 44, 'Unhealthy': 80},
        'Activities': {'Active': 18, 'Moderate': 42, 'Sedentary': 78}
    }
    rows = []
    for key, rule in mappings.items():
        raw = row.get(key, "Unknown")
        score = rule.get(raw, 50)
        rows.append({"Category": key, "Status": str(raw), "RiskScore": score})
    return pd.DataFrame(rows)

def collect_risk_flags(row):
    flags = []
    result_bp = row.get('Result_BP')
    if isinstance(result_bp, str) and result_bp.lower() == 'high':
        flags.append(('Blood pressure assessment indicates high risk.', 'danger'))
    result_chol = row.get('Result_cholesterol')
    if isinstance(result_chol, str) and result_chol.lower() == 'high':
        flags.append(('Cholesterol profile is elevated.', 'warning'))
    result_hba1c = row.get('Result_HbA1c')
    if isinstance(result_hba1c, str) and result_hba1c.lower() == 'high':
        flags.append(('HbA1c levels above recommended threshold.', 'warning'))
    return flags

def classify_bmi(bmi_val: Optional[float]) -> Tuple[str, str]:
    if bmi_val is None or math.isnan(bmi_val):
        return ("No data", "info")
    if bmi_val < 18.5:
        return ("Underweight", "warning")
    if bmi_val < 25:
        return ("Healthy", "info")
    if bmi_val < 30:
        return ("Overweight", "warning")
    return ("Obese", "danger")

def format_bp_badge(row) -> Optional[str]:
    try:
        systolic = row.get('Systolic BP(mmHg)')
        diastolic = row.get('Diastolic(mmHg)')
        if systolic is None or diastolic is None:
            return None
        systolic_val = int(float(systolic))
        diastolic_val = int(float(diastolic))
        return f"{systolic_val}/{diastolic_val} mmHg"
    except (TypeError, ValueError):
        return None

def format_ldl_badge(row) -> Optional[str]:
    try:
        ldl = row.get('LDL (mg/dL)')
        if ldl is None or (isinstance(ldl, float) and math.isnan(ldl)):
            return None
        ldl_val = float(ldl)
        if ldl_val.is_integer():
            ldl_val = int(ldl_val)
        return f"LDL {ldl_val} mg/dL"
    except (TypeError, ValueError):
        return None

def format_hba1c_badge(row) -> Optional[str]:
    try:
        hba1c_val = row.get('HbA1c')
        if hba1c_val is None or (isinstance(hba1c_val, float) and math.isnan(hba1c_val)):
            return None
        value = float(hba1c_val)
        return f"{value:.1f} %"
    except (TypeError, ValueError):
        return None

def create_bar_chart(row: pd.Series, mapping: list[tuple[str, str]], title: str, color_scheme: str = "teal") -> Optional[px.bar]:
    data = []
    for label, key in mapping:
        value = row.get(key)
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue
        if math.isnan(numeric_value):
            continue
        data.append({"Metric": label, "Value": numeric_value})
    if not data:
        return None
    df = pd.DataFrame(data)
    colors = px.colors.sequential.Teal if color_scheme == "teal" else px.colors.sequential.Sunset
    fig = px.bar(
        df,
        x="Metric",
        y="Value",
        text="Value",
        color="Metric",
        color_discrete_sequence=colors
    )
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    fig.update_layout(
        title=title,
        yaxis_title="",
        xaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=30),
        showlegend=False
    )
    return fig

def create_test_timeline(row: pd.Series) -> Optional[px.scatter]:
    mapping = [
        ("Blood Pressure", 'Test Date BP'),
        ("Cholesterol", 'Test Date Chol'),
        ("HbA1c", 'Test Date HbA1c')
    ]
    entries = []
    for label, key in mapping:
        date_val = row.get(key)
        if not date_val:
            continue
        try:
            ts = pd.to_datetime(date_val)
        except (TypeError, ValueError):
            continue
        entries.append({"Metric": label, "Date": ts})
    if not entries:
        return None
    df = pd.DataFrame(entries)
    fig = px.scatter(
        df,
        x="Date",
        y="Metric",
        color="Metric",
        size=[14] * len(df),
        color_discrete_sequence=px.colors.sequential.Bluered
    )
    fig.update_layout(
        title="Recent Test Timeline",
        yaxis_title="",
        xaxis_title="Date",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=30),
        showlegend=False
    )
    fig.update_traces(marker=dict(symbol="circle", line=dict(width=2, color="white")))
    return fig

st.sidebar.markdown("### Patient Lookup")
st.sidebar.caption("Provide an NHS identifier to view personalised guidance.")
patNhs = st.sidebar.text_input("Enter Patient ID: ", help="Numbers only, e.g. 9627747619")
patNhs_clean = patNhs.strip()
if patNhs_clean:
    if not patNhs_clean.isdigit():
        st.error("Please enter a numeric NHS Patient ID.")
        st.stop()

    patient_id = int(patNhs_clean)

    try:
        with st.spinner("Fetching patient data and generating AI insights..."):
            respData = get_ai_response(patient_id)
        st.success(f"MedAssistant insights ready for NHS ID {patient_id}.")
    except Exception as exc:
        st.error("Unable to retrieve AI response. Please try again later.")
        st.caption(f"Details: {exc}")
        st.stop()

    ptTbl = respData['PatientInfo']
    base_row = ptTbl.iloc[0]
    bm = ptTbl[['Weight(kg)', 'Height(cm)']].copy()
    heightM = bm['Height(cm)']*0.01
    heightVal = (heightM*heightM).replace(0, float('nan'))
    bm['BMI'] = (bm['Weight(kg)']/heightVal).round(2)
    bmi_value = bm['BMI'].iloc[0] if not bm['BMI'].isna().all() else None
    bmi_display = (
        f"{bmi_value:.1f}"
        if isinstance(bmi_value, numbers.Real) and not math.isnan(bmi_value)
        else "N/A"
    )
    bmi_badge, bmi_badge_level = classify_bmi(bmi_value)
    risk_flags = collect_risk_flags(base_row)
    bmi_pill_class = "good" if bmi_badge_level == "info" else ("warn" if bmi_badge_level == "warning" else "bad")
    risk_scores = score_vitals_risk(base_row, bmi_value)
    wellness_score = None
    if risk_scores:
        avg_risk = sum(item["Score"] for item in risk_scores) / len(risk_scores)
        wellness_score = max(0, 100 - int(avg_risk))

    hero = textwrap.dedent(
        f"""
        <div class="hero">
            <div style="flex:1;">
                <div class="eyebrow">NHS MedAssist</div>
                <h1>Clinical cockpit for patient {patient_id}</h1>
                <div class="subtitle">AI-assisted overview aligned to NICE guidance. Review risks, vitals, and lifestyle signals at a glance.</div>
                <div class="meta">
                    <span class="pill">Age {base_row.get('Age','N/A')}</span>
                    <span class="pill">{base_row.get('Gender','N/A')}</span>
                    <span class="pill">{base_row.get('Ethnicity','N/A')}</span>
                    <span class="pill {bmi_pill_class}">BMI {bmi_display}</span>
                </div>
            </div>
            <div class="stat-grid">
                {render_metric_card("Blood Pressure", base_row.get('Result_BP', 'N/A'), badge=format_bp_badge(base_row), badge_level="danger" if str(base_row.get('Result_BP', '')).lower() == 'high' else "info")}
                {render_metric_card("Cholesterol", base_row.get('Result_cholesterol', 'N/A'), badge=format_ldl_badge(base_row), badge_level="warning" if str(base_row.get('Result_cholesterol', '')).lower() == 'high' else "info")}
                {render_metric_card("HbA1c", base_row.get('Result_HbA1c', 'N/A'), badge=format_hba1c_badge(base_row), badge_level="warning" if str(base_row.get('Result_HbA1c', '')).lower() == 'high' else "info")}
                {render_metric_card("Wellness Index", f"{wellness_score} / 100" if wellness_score is not None else "N/A", badge="Lower = healthier" if wellness_score is not None else None, badge_level="info")}
            </div>
        </div>
        """
    ).strip()
    st.markdown(hero, unsafe_allow_html=True)

    bp_chart = create_bar_chart(
        base_row,
        [
            ("Systolic", 'Systolic BP(mmHg)'),
            ("Diastolic", 'Diastolic(mmHg)'),
            ("Heart Rate", 'Heart rate')
        ],
        "Cardiovascular Snapshot",
        color_scheme="teal"
    )
    chol_chart = create_bar_chart(
        base_row,
        [
            ("HDL", 'HDL (mg/dL)'),
            ("LDL", 'LDL (mg/dL)'),
            ("Triglycerides", 'Triglycerides (mg/dL)'),
            ("Total Chol", 'TotChol (mg/dL)')
        ],
        "Cholesterol Profile",
        color_scheme="sunset"
    )
    hba1c_chart = create_bar_chart(
        base_row,
        [
            ("HbA1c %", 'HbA1c')
        ],
        "Glycemic Control Snapshot",
        color_scheme="teal"
    )
    timeline_chart = create_test_timeline(base_row)

    tab1,tab2 = st.tabs(['Response','NICE'])
    with tab1:
        overview_tab, clinical_tab, lifestyle_tab, ai_tab = st.tabs(
            ['Overview', 'Clinical Dashboard', 'Lifestyle & History', 'AI Guidance']
        )

        with overview_tab:
            st.markdown("### Patient Snapshot")
            summary_cols = st.columns(4)
            summary_cols[0].markdown(render_metric_card("Age", base_row.get('Age', 'N/A')), unsafe_allow_html=True)
            summary_cols[1].markdown(render_metric_card("Gender", base_row.get('Gender', 'N/A')), unsafe_allow_html=True)
            summary_cols[2].markdown(render_metric_card("Ethnicity", base_row.get('Ethnicity', 'N/A')), unsafe_allow_html=True)
            summary_cols[3].markdown(
                render_metric_card("BMI", bmi_display, badge=bmi_badge, badge_level=bmi_badge_level),
                unsafe_allow_html=True
            )

            viz_cols = st.columns(2)
            if risk_scores:
                radar_df = pd.DataFrame(risk_scores)
                blue_red_colors = px.colors.sequential.Bluered
                radar_color = blue_red_colors[-2] if blue_red_colors else "#3b82f6"
                radar_fig = px.line_polar(
                    radar_df,
                    r="Score",
                    theta="Metric",
                    line_close=True,
                    color_discrete_sequence=[radar_color]
                )
                radar_fig.update_traces(fill="toself")
                radar_fig.update_layout(
                    title="Risk Radar (higher = riskier)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    polar=dict(
                        radialaxis=dict(range=[0, 100])
                    ),
                    margin=dict(l=10, r=10, t=50, b=10)
                )
                viz_cols[0].plotly_chart(radar_fig, use_container_width=True)
            else:
                viz_cols[0].info("Not enough vitals to build a risk radar.")

            lifestyle_df = lifestyle_scores(base_row)
            if not lifestyle_df.empty:
                life_fig = px.bar(
                    lifestyle_df,
                    x="RiskScore",
                    y="Category",
                    orientation="h",
                    color="Category",
                    text="Status",
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                life_fig.update_layout(
                    title="Lifestyle Risk Snapshot",
                    xaxis_title="Risk score (higher = riskier)",
                    yaxis_title="",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=50, b=30),
                    showlegend=False
                )
                viz_cols[1].plotly_chart(life_fig, use_container_width=True)
            else:
                viz_cols[1].info("Lifestyle data unavailable.")

            status_cols = st.columns(3)
            status_cols[0].markdown(
                render_metric_card(
                    "Blood Pressure",
                    base_row.get('Result_BP', 'N/A'),
                    badge=format_bp_badge(base_row),
                    badge_level="danger" if str(base_row.get('Result_BP', '')).lower() == 'high' else "info"
                ),
                unsafe_allow_html=True
            )
            status_cols[1].markdown(
                render_metric_card(
                    "Cholesterol",
                    base_row.get('Result_cholesterol', 'N/A'),
                    badge=format_ldl_badge(base_row),
                    badge_level="warning" if str(base_row.get('Result_cholesterol', '')).lower() == 'high' else "info"
                ),
                unsafe_allow_html=True
            )
            status_cols[2].markdown(
                render_metric_card(
                    "HbA1c",
                    base_row.get('Result_HbA1c', 'N/A'),
                    badge=format_hba1c_badge(base_row),
                    badge_level="warning" if str(base_row.get('Result_HbA1c', '')).lower() == 'high' else "info"
                ),
                unsafe_allow_html=True
            )

            if risk_flags:
                st.markdown("#### Key Alerts")
                for message, level in risk_flags:
                    tone = "bad" if level == "danger" else "warn"
                    st.markdown(f'<div class="callout {"warn" if tone=="warn" else ""}">{message}</div>', unsafe_allow_html=True)

        with clinical_tab:
            st.markdown("### Clinical Metrics Dashboard")
            chart_cols = st.columns(2)
            if bp_chart:
                chart_cols[0].plotly_chart(bp_chart, use_container_width=True)
            else:
                chart_cols[0].info("Insufficient blood pressure data to visualise.")

            if chol_chart:
                chart_cols[1].plotly_chart(chol_chart, use_container_width=True)
            else:
                chart_cols[1].info("Insufficient cholesterol data to visualise.")

            chart_cols_secondary = st.columns(2)
            if hba1c_chart:
                chart_cols_secondary[0].plotly_chart(hba1c_chart, use_container_width=True)
            else:
                chart_cols_secondary[0].info("No HbA1c value recorded.")

            if timeline_chart:
                chart_cols_secondary[1].plotly_chart(timeline_chart, use_container_width=True)
            else:
                chart_cols_secondary[1].info("Test timeline data unavailable.")

            st.markdown("#### Clinical Tables")
            metrics_cols = st.columns(2)
            with metrics_cols[0]:
                with st.expander("Body Measurements", expanded=True):
                    st.dataframe(bm.reset_index(drop=True).style.applymap(color_bmi,subset=['BMI']),
                                 hide_index=True,use_container_width=True)
                bp = ptTbl[['Systolic BP(mmHg)', 'Diastolic(mmHg)', 'Heart rate', 'Result_BP']]
                with st.expander("Blood Pressure & Heart Rate", expanded=False):
                    st.dataframe(bp.reset_index(drop=True).style.applymap(color_bp,subset=['Result_BP']),hide_index=True,use_container_width=True)
            with metrics_cols[1]:
                chol = ptTbl[['HDL (mg/dL)', 'LDL (mg/dL)', 'TotChol (mg/dL)','Triglycerides (mg/dL)', 'Result_cholesterol']]
                with st.expander("Cholesterol Profile", expanded=True):
                    st.dataframe(chol.style.applymap(color_bp,subset=['Result_cholesterol']),
                                 hide_index=True,use_container_width=True)
                hba1c = ptTbl[['HbA1c', 'Result_HbA1c']]
                with st.expander("Glycemic Control", expanded=False):
                    st.dataframe(hba1c,hide_index=True,use_container_width=True)
                testPeriod = ptTbl[['Test Date BP','Test Date Chol','Test Date HbA1c']]
                with st.expander("Recent Test Dates", expanded=False):
                    st.dataframe(testPeriod,hide_index=True,use_container_width=True)

        with lifestyle_tab:
            st.subheader("Lifestyle & Background")
            habits = ptTbl[['Smoking', 'Drinking', 'Food habits', 'Activities']]
            st.markdown("#### Lifestyle Indicators")
            st.dataframe(habits.reset_index(drop=True).style.applymap(color_habits),
                            hide_index=True,use_container_width=True)

            caseHist = ptTbl[['Family history', 'Ongoing disease', 'Ongoing medications']]
            st.markdown("#### Medical History")
            st.dataframe(caseHist.reset_index(drop=True).style.applymap(color_hist,subset=['Family history']),
                         hide_index=True,use_container_width=True)

        with ai_tab:
            st.subheader("MedAssistant Treatment Suggestions")
            st.caption("Generated by Azure OpenAI using the patient's data and relevant NICE guidance.")
            st.code(respData['AIResp'])
            st.download_button(
                label="Download AI Recommendations",
                data=respData['AIResp'],
                file_name=f"medassistant_{patient_id}_recommendations.txt",
                mime="text/plain",
                use_container_width=True
            )
            show_raw = st.toggle("Show raw patient payload", key="show_raw_payload", value=False)
            if show_raw:
                st.json(ptTbl.to_dict(orient='records')[0])

    with tab2:
        st.write('Key NICE Guidelines Info:')
        st.text_area(
            "Summary of NICE guidance",
            respData['NICE'],
            height=400,
            disabled=True
        )
else:
    st.markdown(
        textwrap.dedent(
            """
            <div class="empty-state">
                <h3>MedAssist Clinical Cockpit</h3>
                <p>Enter an NHS patient number in the sidebar to load vitals, labs, and AI guidance with the new experience.</p>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True
    )
