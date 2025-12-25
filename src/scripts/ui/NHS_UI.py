import math
import numbers
import os,sys
from typing import Optional, Tuple
import pandas as pd
import plotly.express as px
import streamlit as st

path = os.getcwd()
sys.path.append(path)
from src.scripts.models.azureOpenAI_st import aiResp

st.set_page_config(layout='wide',
                   page_title='AI MedAssitant',
                   )

CODE_BLOCK_STYLE = """
    <style>
        pre code, code {
            white-space: pre-wrap !important;
            word-break: break-word;
        }
        .metric-card {
            background: rgba(49, 51, 63, 0.08);
            border-radius: 0.75rem;
            padding: 0.9rem 1.1rem;
            border: 1px solid rgba(250, 250, 250, 0.1);
        }
        .metric-card h4 {
            margin: 0;
            font-size: 0.85rem;
            color: #6d7d8b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-card p {
            margin: 0.2rem 0 0;
            font-size: 1.6rem;
            font-weight: 600;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: rgba(28, 131, 225, 0.15);
            color: #1c83e1;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge--warning {
            background: rgba(255, 159, 67, 0.16);
            color: #cc6c00;
        }
        .badge--danger {
            background: rgba(234, 67, 53, 0.18);
            color: #a52714;
        }
    </style>
"""

st.markdown(CODE_BLOCK_STYLE, unsafe_allow_html=True)

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
    return f"""
        <div class="metric-card">
            <h4>{title}</h4>
            <p>{value}</p>
            {badge_html}
        </div>
    """

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
            st.subheader("Patient Snapshot")
            summary_cols = st.columns(4)
            summary_cols[0].markdown(render_metric_card("Age", base_row.get('Age', 'N/A')), unsafe_allow_html=True)
            summary_cols[1].markdown(render_metric_card("Gender", base_row.get('Gender', 'N/A')), unsafe_allow_html=True)
            summary_cols[2].markdown(render_metric_card("Ethnicity", base_row.get('Ethnicity', 'N/A')), unsafe_allow_html=True)
            summary_cols[3].markdown(
                render_metric_card("BMI", bmi_display, badge=bmi_badge, badge_level=bmi_badge_level),
                unsafe_allow_html=True
            )

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
                    if level == 'danger':
                        st.error(message)
                    else:
                        st.warning(message)

        with clinical_tab:
            st.subheader("Clinical Metrics Dashboard")
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
    st.write("Enter the Patient NHS Number to generate the appropriate response.")
