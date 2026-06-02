import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="ERIA - Education Regulation Impact Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main Header Section
st.markdown("""
    <style>
    /* Full page background overlay container */
    .header-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 25px;
        border: 1px solid #334155;
    }
    /* Vibrant Title styling */
    .eria-title {
        font-size: 40px;
        font-weight: 800;
        background: linear-gradient(135deg, #60A5FA 0%, #34D399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 0px;
        margin-bottom: 10px;
        font-family: 'Inter', sans-serif;
    }
    /* Crisp Subtitle styling */
    .eria-subtitle {
        font-size: 18px;
        font-weight: 500;
        color: #94A3B8;
        margin-bottom: 0px;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# Render everything packaged inside the attractive colored background container
st.markdown("""
    <div class="header-container">
        <h1 class="eria-title">🎓 Education Regulation Impact Analyzer (ERIA)</h1>
        <p class="eria-subtitle">Simplifying Education Policies and Circulars for Every Institution</p>
    </div>
""", unsafe_allow_html=True)


# Layout: Split into two columns
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📌 Project Overview")
    st.write(
        "ERIA is an advanced EdTech and Policy Analytics platform. "
        "It automatically tracks, processes, and analyzes complex legislative documents, "
        "parliamentary bills, and educational circulars. "
        "The system translates dense legal jargon into actionable institutional insights."
    )
    
    st.header("🎯 Core Value Proposition")
    st.markdown("- **Automated Compliance:** Reduces manual tracking of ministry updates.")
    st.markdown("- **Risk Mitigation:** Alerts institutions to upcoming regulatory deadlines.")
    st.markdown("- **Strategic Planning:** Maps short, medium, and long-term impacts.")

with col2:
    st.header("🛠️ Skills & Technologies Covered")
    
    with st.expander("Data Pipelines", expanded=True):
        st.markdown("- **Web Scraping:** Extracting bills from Sansad portals.")
        st.markdown("- **Document Ingestion:** Processing PDF and HTML sources.")
        st.markdown("- **NLP Processing:** Cleaning and preprocessing text data.")

    with st.expander("Analytics & AI", expanded=True):
        st.markdown("- **Topic Extraction:** Identifying core legislative themes.")
        st.markdown("- **Dependency Graphs:** Mapping timelines and policy linkages.")
        st.markdown("- **LLM Summarization:** Generating bite-sized compliance action items.")

    with st.expander("Workflow & UI", expanded=True):
        st.markdown("- **Langflow:** Designing complex AI agent workflows.")
        st.markdown("- **Streamlit:** Deploying interactive data dashboards.")

# Footer / Quick Action Status
st.markdown("---")
st.info("💡 **Getting Started:** Use the sidebar to upload a new circular or view current impact timelines.")
