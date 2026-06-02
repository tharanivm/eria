import os
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

# --- Page Configuration ---
st.set_page_config(
    page_title="EduReg Premium Insights Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global Style Injection (Matches Modern Card UI & Fixes Word Wrap) ---
st.markdown("""
    <style>
    /* Main UI Accents */
    .title-area { font-size: 2.2rem; font-weight: 700; color: #F3F4F6; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 10px; }
    
    /* Top Row Metric Cards */
    .kpi-container { display: flex; gap: 20px; margin-bottom: 2rem; width: 100%; }
    .kpi-card { background: #1E293B; border: 1px solid #334155; padding: 1.2rem; border-radius: 12px; flex: 1; min-width: 150px; }
    .kpi-label { font-size: 0.85rem; color: #94A3B8; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-val { font-size: 1.6rem; font-weight: 700; color: #38BDF8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    
    /* Document Overview Table Styling */
    .overview-table { width: 100%; border-collapse: collapse; background: #1E293B; border-radius: 12px; overflow: hidden; }
    .overview-table td { padding: 12px 16px; border-bottom: 1px solid #334155; color: #E2E8F0; font-size: 14px; vertical-align: top; }
    .overview-table td.label { font-weight: 600; color: #94A3B8; width: 35%; }
    .badge-positive { background: #065F46; color: #34D399; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; }
    .badge-negative { background: #991B1B; color: #F87171; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; }
    
    /* Native Dataframe Overrides to Force Perfect Word Wrapping */
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
st.sidebar.title("🛠️ Control Center")
gemini_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
if not gemini_api_key:
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

# --- Core Logic Functions ---
def init_gemini_client(api_key):
    try: return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to connect client: {str(e)}")
        return None

def analyze_document_with_gemini(client, file_bytes, mime_type):
    """Uses Gemini 2.5 Flash to extract both unstructured metrics & structured tables."""
    prompt = """
    You are an expert compliance & legal framework data parser. 
    Analyze the attached document and break your output strictly into these 6 marked sections using the exact headers provided below.

    ## SECTION 1: HEADER METRICS
    Document Title: [Provide official clear short title]
    Issuing Body: [Provide exact clean organization name]
    Topic Category: [Faculty Policy, Curriculum, Administrative, Finance etc.]
    Sentiment: [Positive / Neutral / Negative]
    Risk Level: [Low / Medium / High]
    Regulation Date: [Provide exact date or 'January 1, 2024' style format]

    ## SECTION 2: SUMMARY & OVERVIEW
    [Provide a clean paragraph detail summarizing the fundamental baseline meaning of the document]

    ## SECTION 3: STAKEHOLDER IMPACT
    Stakeholder Vector | Benefits Realized | Operational Constraints | Strategic Opportunities
    Students | [Text] | [Text] | [Text]
    Faculty | [Text] | [Text] | [Text]
    Institutions | [Text] | [Text] | [Text]
    Administrators | [Text] | [Text] | [Text]

    ## SECTION 4: IMPACT ASSESSMENT
    Horizon Vector | Primary Impacts Inferred | Strategic Compliance Action Required
    Short Term (0-1 Year) | [Text] | [Text]
    Medium Term (1-5 Years) | [Text] | [Text]
    Long Term (>5 Years) | [Text] | [Text]

    ## SECTION 5: RISKS & OPPORTUNITIES
    Factor Matrix Variable | Identified Vulnerability Details | Mitigation Framework Strategy
    Controversial Elements | [Text] | [Text]
    Implementation Roadblocks | [Text] | [Text]
    Operational Vulnerabilities | [Text] | [Text]

    ## SECTION 6: CHRONOLOGY
    Timeline Milestone Block | Historical Circular Context Reference | Long-Term Strategic System Shift
    Legacy Frameworks | [Text] | [Text]
    Current Target Mandate | [Text] | [Text]
    Future Alignment Horizon | [Text] | [Text]
    """

    try:
        document_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[document_part, prompt]
        )
        return response.text
    except Exception as e:
        st.error(f"Analysis engine error: {str(e)}")
        return None



def parse_sections(text):
    """Splits raw model outputs cleanly by explicit structural section keys."""
    sections = {"metrics": "", "summary": "", "stakeholder": "", "impact": "", "risk": "", "chronology": ""}
    if not text: return sections
    try:
        parts = text.split("## SECTION ")
        for part in parts:
            if part.startswith("1: HEADER METRICS"): sections["metrics"] = part.replace("1: HEADER METRICS", "").strip()
            elif part.startswith("2: SUMMARY & OVERVIEW"): sections["summary"] = part.replace("2: SUMMARY & OVERVIEW", "").strip()
            elif part.startswith("3: STAKEHOLDER IMPACT"): sections["stakeholder"] = part.replace("3: STAKEHOLDER IMPACT", "").strip()
            elif part.startswith("4: IMPACT ASSESSMENT"): sections["impact"] = part.replace("4: IMPACT ASSESSMENT", "").strip()
            elif part.startswith("5: RISKS & OPPORTUNITIES"): sections["risk"] = part.replace("5: RISKS & OPPORTUNITIES", "").strip()
            elif part.startswith("6: CHRONOLOGY"): sections["chronology"] = part.replace("6: CHRONOLOGY", "").strip()
    except Exception as e:
        st.error(f"Section parser dropped stream packet: {e}")
    return sections

def parse_header_metrics(metrics_text):
    """Parses raw text key-values into a usable application dictionary."""
    metrics_dict = {"title": "Unknown", "body": "Unknown", "category": "Unknown", "sentiment": "Neutral", "risk": "Low", "date": "N/A"}
    for line in metrics_text.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            key, val = key.lower().strip(), val.strip()
            if "title" in key: metrics_dict["title"] = val
            elif "issuing" in key: metrics_dict["body"] = val
            elif "category" in key: metrics_dict["category"] = val
            elif "sentiment" in key: metrics_dict["sentiment"] = val
            elif "risk" in key: metrics_dict["risk"] = val
            elif "date" in key: metrics_dict["date"] = val
    return metrics_dict



def convert_markdown_table_to_df(md_table_text):
    """Extracts raw markdown data lines directly into structured native Pandas frames."""
    try:
        lines = [line.strip() for line in md_table_text.strip().split("\n") if line.strip()]
        if len(lines) < 2: return pd.DataFrame()
        headers = [cell.strip() for cell in lines[0].split("|") if cell.strip()]
        data_rows = []
        start_idx = 2 if "---" in lines[1] else 1
        for line in lines[start_idx:]:
            row = [cell.strip() for cell in line.split("|")]
            if line.startswith("|"): row = row[1:]
            if line.endswith("|"): row = row[:-1]
            if len(row) >= len(headers): data_rows.append(row[:len(headers)])
        return pd.DataFrame(data_rows, columns=headers)
    except Exception:
        return pd.DataFrame({"Data Process Matrix": ["Parsing matrix realignment in process..."]})

# --- Application Layout Rendering Pipeline ---
st.markdown("### Ingest Source Document")
uploaded_file = st.file_uploader("Upload Circular Document (PDF Format Only)", type=["pdf"])

if uploaded_file is not None:
    if not gemini_api_key:
        st.warning("⚠️ Enter your Gemini API Key in the configuration sidebar to activate the structural parser.")
    else:
        if st.button("🚀 Execute Premium Document Analysis", type="primary"):
            with st.spinner("Compiling strategic document landscape..."):
                client = init_gemini_client(gemini_api_key)
                if client:
                    file_bytes = uploaded_file.read()
                    raw_analysis = analyze_document_with_gemini(client, file_bytes, uploaded_file.type)
                    if raw_analysis:
                        st.session_state['panel_data'] = parse_sections(raw_analysis)
                        st.success("✅ Analysis matrices successfully rendered.")

# --- Render Analysis Output Dashboard Canvas ---
if 'panel_data' in st.session_state:
    data = st.session_state['panel_data']
    meta = parse_header_metrics(data["metrics"])
    
    st.markdown("---")
    
    # 1. Premium Top Banner Title Area
    st.markdown(f'<div class="title-area">📊 Analysis: {meta["title"]}</div>', unsafe_allow_html=True)
    
    # 2. Top row KPI Metric Cards Layout
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card"><div class="kpi-label">Issuing Body</div><div class="kpi-val" title="{meta["body"]}">{meta["body"]}</div></div>
        <div class="kpi-card"><div class="kpi-label">Topic Category</div><div class="kpi-val" title="{meta["category"]}">{meta["category"]}</div></div>
        <div class="kpi-card"><div class="kpi-label">Sentiment</div><div class="kpi-val" style="color: #34D399;">{meta["sentiment"]}</div></div>
        <div class="kpi-card"><div class="kpi-label">Risk Level</div><div class="kpi-val" style="color: #F87171;">{meta["risk"]}</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    import plotly.graph_objects as go

    # --- Gauge Conversion Logic ---
    sentiment_score_map = {
        "positive": 85,
        "neutral": 55,
        "negative": 25
    }

    risk_score_map = {
        "low": 20,
        "medium": 55,
        "high": 90
    }

    sentiment_score = sentiment_score_map.get(meta["sentiment"].lower(), 50)
    risk_score = risk_score_map.get(meta["risk"].lower(), 50)

    # --- Gauge Layout ---
    g1, g2 = st.columns(2)

    with g1:
        sentiment_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sentiment_score,
            title={'text': "Sentiment Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#10B981"},
                'steps': [
                    {'range': [0, 35], 'color': "#7F1D1D"},
                    {'range': [35, 70], 'color': "#78350F"},
                    {'range': [70, 100], 'color': "#064E3B"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': sentiment_score
                }
            }
        ))

        sentiment_fig.update_layout(
            height=320,
            paper_bgcolor="#0F172A",
            font={'color': "white"}
        )

        st.plotly_chart(sentiment_fig, use_container_width=True)

    with g2:
        risk_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Risk Level Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#EF4444"},
                'steps': [
                    {'range': [0, 35], 'color': "#064E3B"},
                    {'range': [35, 70], 'color': "#78350F"},
                    {'range': [70, 100], 'color': "#7F1D1D"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': risk_score
                }
            }
        ))

        risk_fig.update_layout(
            height=320,
            paper_bgcolor="#0F172A",
            font={'color': "white"}
        )

        st.plotly_chart(risk_fig, use_container_width=True)
        
    # --- Style Injection Upgrades for Grid Card Framework ---
    st.markdown("""
        <style>
        /* Card Canvas Blocks Wrapper */
        .dashboard-grid { display: flex; gap: 20px; margin-bottom: 20px; width: 100%; }
        .dashboard-card { background: #1E293B; border: 1px solid #334155; border-radius: 12px; flex: 1; padding: 0rem; overflow: hidden; }
        
        /* Specialized Card Header Accents */
        .card-hdr { padding: 12px 16px; font-weight: 700; font-size: 15px; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 8px; }
        .hdr-green { background: rgba(16, 185, 129, 0.1); color: #10B981; border-top: 3px solid #10B981; }
        .hdr-red { background: rgba(239, 68, 68, 0.1); color: #EF4444; border-top: 3px solid #EF4444; }
        .hdr-blue { background: rgba(59, 130, 246, 0.1); color: #3B82F6; border-top: 3px solid #3B82F6; }
        .hdr-yellow { background: rgba(245, 158, 11, 0.1); color: #F59E0B; border-top: 3px solid #F59E0B; }
        
        /* Inside Bullet Point Framework Wrapper */
        .card-body { padding: 16px; min-height: 180px; }
        .card-body ul { margin: 0; padding-left: 20px; color: #E2E8F0; font-size: 14px; line-height: 1.6; }
        .card-body li { margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)
    





    # --- Restructured Tab Panels Layout Engine ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary",
        "👥 Stakeholder Impact",
        "✔️ Impact Assessment",
        "⚠️ Risks & Opportunities",
        "📅 Chronology"
    ])
    
    # --- TAB 1: EXECUTIVE SUMMARY PANEL (Original Dual Column View) ---
    with tab1:
        grid_col1, grid_col2 = st.columns([1.2, 1.8])
        with grid_col1:
            st.markdown("#### 📄 Document Overview")
            badge_class = "badge-positive" if "positive" in meta["sentiment"].lower() else "badge-negative"
            st.markdown(f"""
            <table class="overview-table">
                <tr><td class="label">Issuing Body</td><td>{meta["body"]}</td></tr>
                <tr><td class="label">Category</td><td>{meta["category"]}</td></tr>
                <tr><td class="label">Regulation Date</td><td>{meta["date"]}</td></tr>
                <tr><td class="label">Sentiment</td><td><span class="{badge_class}">{meta["sentiment"]}</span></td></tr>
            </table>
            """, unsafe_allow_html=True)
        with grid_col2:
            st.markdown("#### 🔍 Executive Brief")
            st.info(data["summary"] if data["summary"] else "Comprehensive breakdown overview updating details...")
            
    # --- TAB 2: STAKEHOLDER IMPACT PANEL (Grid Layout Mapping) ---
    with tab2:
        df_stakeholder = convert_markdown_table_to_df(data["stakeholder"])
        
        # Build individual text strings for bullet lists securely from df
        students_notes = ""
        faculty_notes = ""
        institutions_notes = ""
        admins_notes = ""
        
        for idx, row in df_stakeholder.iterrows():
            role = str(row.iloc[0]).lower()
            val_str = f"<li><b>{row.keys()[1]}:</b> {row.iloc[1]} | <b>{row.keys()[2]}:</b> {row.iloc[2]}</li>"
            if "student" in role: students_notes += val_str
            elif "faculty" in role: faculty_notes += val_str
            elif "institution" in role: institutions_notes += val_str
            else: admins_notes += val_str

        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-hdr hdr-green">👥 Student Vectors</div>
                <div class="card-body"><ul>{students_notes if students_notes else "<li>Updates pending...</li>"}</ul></div>
            </div>
            <div class="dashboard-card">
                <div class="card-hdr hdr-red">👨‍🏫 Faculty Vectors</div>
                <div class="card-body"><ul>{faculty_notes if faculty_notes else "<li>Updates pending...</li>"}</ul></div>
            </div>
        </div>
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-hdr hdr-blue">🏢 Institutional Impact</div>
                <div class="card-body"><ul>{institutions_notes if institutions_notes else "<li>Updates pending...</li>"}</ul></div>
            </div>
            <div class="dashboard-card">
                <div class="card-hdr hdr-yellow">⚙️ Admin Adjustments</div>
                <div class="card-body"><ul>{admins_notes if admins_notes else "<li>Updates pending...</li>"}</ul></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    # --- TAB 3: IMPACT ASSESSMENT HORIZON PANEL (Grid Layout Mapping) ---
    with tab3:
        df_impact = convert_markdown_table_to_df(data["impact"])
        short_term, med_term, long_term = "", "", ""
        
        for idx, row in df_impact.iterrows():
            horizon = str(row.iloc[0]).lower()
            val_str = f"<li>{row.iloc[1]} — <i>{row.iloc[2]}</i></li>"
            if "short" in horizon or "0-1" in horizon: short_term += val_str
            elif "medium" in horizon or "1-5" in horizon: med_term += val_str
            else: long_term += val_str

        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-hdr hdr-green">⏳ Short Term (0-1 Year)</div>
                <div class="card-body"><ul>{short_term if short_term else "<li>Immediate setups initialization...</li>"}</ul></div>
            </div>
            <div class="dashboard-card">
                <div class="card-hdr hdr-blue">⏳ Medium Term (1-5 Years)</div>
                <div class="card-body"><ul>{med_term if med_term else "<li>System integration alignments...</li>"}</ul></div>
            </div>
            <div class="dashboard-card">
                <div class="card-hdr hdr-yellow">⏳ Long Term (>5 Years)</div>
                <div class="card-body"><ul>{long_term if long_term else "<li>Systemic transformational changes...</li>"}</ul></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    # --- TAB 4: RISKS & OPPORTUNITIES PANEL (Exact Layout of Attached Image) ---
    with tab4:
        df_risk = convert_markdown_table_to_df(data["risk"])
        positives_list, negatives_list, opportunities_list, risks_list = "", "", "", ""
        
        for idx, row in df_risk.iterrows():
            factor = str(row.iloc[0]).lower()
            val_str1 = f"<li>{row.iloc[1]}</li>"
            val_str2 = f"<li>{row.iloc[2]}</li>"
            if "contro" in factor:
                negatives_list += val_str1
                risks_list += val_str2
            elif "roadblock" in factor or "gap" in factor:
                negatives_list += val_str1
                risks_list += val_str2
            else:
                positives_list += val_str1
                opportunities_list += val_str2

        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-hdr hdr-green">✅ Positives</div>
                <div class="card-body"><ul>{positives_list if positives_list else "<li>Enhanced workflow flexibility patterns achieved.</li><li>Strengthened procedural evaluation checks.</li>"}</ul></div>
            </div>
            <div class="dashboard-card">
                <div class="card-hdr hdr-red">❌ Negatives</div>
                <div class="card-body"><ul>{negatives_list if negatives_list else "<li>Increased initial administrative workload overhead.</li><li>Potential logistical deployment adaptation lag.</li>"}</ul></div>
            </div>
        </div>
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-hdr hdr-blue">🚀 Opportunities</div>
                <div class="card-body"><ul>{opportunities_list if opportunities_list else "<li>Strategic adoption of modern automation tools.</li><li>Inter-departmental quality optimization.</li>"}</ul></div>
            </div>
            <div class="dashboard-card">
                <div class="card-hdr hdr-yellow">⚠️ Risks</div>
                <div class="card-body"><ul>{risks_list if risks_list else "<li>Resource constraints across tier-2 infrastructure environments.</li><li>Integration friction with legacy databases.</li>"}</ul></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    # --- TAB 5: CHRONOLOGY PROGRESSION PANEL (Grid Layout Mapping) ---
    with tab5:
        df_chronology = convert_markdown_table_to_df(data["chronology"])
        legacy_context, current_mandate, future_horizon = "", "", ""
        
        for idx, row in df_chronology.iterrows():
            stage = str(row.iloc[0]).lower()
            val_str = f"<li><b>{row.iloc[1]}:</b> {row.iloc[2]}</li>"
            if "legacy" in stage or "predecessor" in stage: legacy_context += val_str
            elif "current" in stage or "target" in stage: current_mandate += val_str
            else: future_horizon += val_str

        st.markdown(f"""
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-hdr hdr-blue">📜 Legacy Context</div>
                <div class="card-body"><ul>{legacy_context if legacy_context else "<li>Predecessor regulatory circular frameworks reference.</li>"}</ul></div>
            </div>
            <div class="dashboard-card">
                <div class="card-hdr hdr-green">🎯 Current Mandate</div>
                <div class="card-body"><ul>{current_mandate if current_mandate else "<li>Active operational transformation directives targets.</li>"}</ul></div>
            </div>
            <div class="dashboard-card">
                <div class="card-hdr hdr-yellow">🔮 Future Alignment</div>
                <div class="card-body"><ul>{future_horizon if future_horizon else "<li>Long term systemic continuous evaluation horizon goals.</li>"}</ul></div>
            </div>
        </div>
        """, unsafe_allow_html=True)