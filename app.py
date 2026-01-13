"""
Aevum - Longevity Analytics Platform
Powered by Titan Protocol v2
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.titan_engine import (
    run_titan_engine, standardize_labs, TITAN_SYSTEMS
)
from modules.data_extraction import pdf_to_dataframe, parse_whoop_csv, create_sample_blood_data

# =============================================================================
# PAGE CONFIG & STYLES
# =============================================================================

st.set_page_config(
    page_title="Aevum",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Light theme with Nunito font - NO EMOJIS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800&display=swap');

/* Base styles - Light theme */
.stApp {
    background: linear-gradient(180deg, #f8f9fc 0%, #eef1f8 100%);
}
* {
    font-family: 'Nunito', sans-serif;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { 
    padding: 2rem 3rem 4rem 3rem; 
    max-width: 1100px; 
}

/* Typography */
h1, h2, h3 {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: #1a1a2e !important;
}

.main-title {
    font-size: 2rem;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.sub-title {
    font-size: 1rem;
    color: #6b7280;
    margin-bottom: 2rem;
    font-weight: 500;
}

/* Logo/Brand mark */
.brand-mark {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
.brand-mark::after {
    content: '';
    width: 16px;
    height: 16px;
    border: 3px solid white;
    border-radius: 50%;
}

/* Cards */
.card {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    margin-bottom: 1rem;
    border: 1px solid rgba(0, 0, 0, 0.04);
}
.card-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.75rem;
}
.card-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: #1a1a2e;
}
.card-subtitle {
    font-size: 0.85rem;
    color: #9ca3af;
    margin-top: 0.25rem;
}

/* Score colors */
.score-optimal { color: #22c55e; }
.score-good { color: #84cc16; }
.score-fair { color: #f59e0b; }
.score-risk { color: #ef4444; }

/* System cards */
.system-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.04);
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
}
.system-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}
.system-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.75rem;
    position: relative;
}
.system-icon::after {
    content: '';
    position: absolute;
    border-radius: 50%;
}
.system-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}
.system-score {
    font-size: 1.75rem;
    font-weight: 800;
    line-height: 1;
}
.system-status {
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* Status badges */
.status-optimal { 
    color: #166534; 
    background: #dcfce7;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
}
.status-good { 
    color: #3f6212; 
    background: #ecfccb;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
}
.status-fair { 
    color: #92400e; 
    background: #fef3c7;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
}
.status-risk { 
    color: #991b1b; 
    background: #fee2e2;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
}

/* System icon styles with shapes */
.icon-heart { 
    background: linear-gradient(135deg, #fecaca, #fca5a5); 
}
.icon-heart::after {
    width: 14px;
    height: 14px;
    background: #ef4444;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
}
.icon-metabolic { 
    background: linear-gradient(135deg, #fed7aa, #fdba74); 
}
.icon-metabolic::after {
    width: 12px;
    height: 12px;
    background: #f97316;
    border-radius: 2px;
    transform: rotate(45deg);
}
.icon-immune { 
    background: linear-gradient(135deg, #bbf7d0, #86efac); 
}
.icon-immune::after {
    width: 14px;
    height: 14px;
    border: 3px solid #22c55e;
    background: transparent;
}
.icon-blood { 
    background: linear-gradient(135deg, #fecdd3, #fda4af); 
}
.icon-blood::after {
    width: 10px;
    height: 10px;
    background: #e11d48;
    border-radius: 50%;
}
.icon-brain { 
    background: linear-gradient(135deg, #c7d2fe, #a5b4fc); 
}
.icon-brain::after {
    width: 14px;
    height: 14px;
    border: 3px solid #6366f1;
    border-radius: 50%;
    background: transparent;
}
.icon-liver { 
    background: linear-gradient(135deg, #fde68a, #fcd34d); 
}
.icon-liver::after {
    width: 12px;
    height: 12px;
    background: #eab308;
    border-radius: 3px;
}
.icon-kidney { 
    background: linear-gradient(135deg, #a5f3fc, #67e8f9); 
}
.icon-kidney::after {
    width: 10px;
    height: 10px;
    background: #06b6d4;
    border-radius: 50%;
}
.icon-hormone { 
    background: linear-gradient(135deg, #e9d5ff, #d8b4fe); 
}
.icon-hormone::after {
    width: 0;
    height: 0;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    border-bottom: 12px solid #a855f7;
    background: transparent;
    border-radius: 0;
}

/* Section headers */
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

/* Insights */
.insight-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    border-left: 4px solid #6366f1;
    font-size: 0.9rem;
    color: #374151;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
}
.insight-card.warning {
    border-left-color: #f59e0b;
    background: #fffbeb;
}
.insight-card.success {
    border-left-color: #22c55e;
    background: #f0fdf4;
}
.insight-icon {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 2px;
}
.insight-icon.info { background: #dbeafe; border: 2px solid #3b82f6; }
.insight-icon.warning { background: #fef3c7; border: 2px solid #f59e0b; }
.insight-icon.success { background: #dcfce7; border: 2px solid #22c55e; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    font-family: 'Nunito', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #4338ca) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
}
.stButton > button:disabled {
    background: #e5e7eb !important;
    color: #9ca3af !important;
}

/* File uploader */
.stFileUploader > div {
    background: #ffffff !important;
    border: 2px dashed #d1d5db !important;
    border-radius: 16px !important;
}
.stFileUploader > div:hover {
    border-color: #6366f1 !important;
    background: #f5f3ff !important;
}

/* Slider */
.stSlider > div > div > div { background: #6366f1 !important; }

/* Number input */
.stNumberInput input {
    background: #ffffff !important;
    border: 2px solid #e5e7eb !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 16px;
    padding: 6px;
    gap: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 12px;
    color: #6b7280;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    font-family: 'Nunito', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: #ffffff;
}

/* Messages */
.upload-success {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    color: #166534;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.upload-success::before {
    content: '';
    width: 18px;
    height: 18px;
    background: #22c55e;
    border-radius: 50%;
    flex-shrink: 0;
}
.upload-error {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    color: #991b1b;
}
.upload-info {
    background: #eff6ff;
    border: 1px solid #93c5fd;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    color: #1e40af;
    font-weight: 600;
}

/* Bio age display */
.bio-age-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    border: 2px solid #dcfce7;
}
.bio-age-value {
    font-size: 3.5rem;
    font-weight: 800;
    color: #166534;
    line-height: 1;
}
.bio-age-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #22c55e;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}
.bio-age-card.older {
    border-color: #fecaca;
}
.bio-age-card.older .bio-age-value {
    color: #991b1b;
}
.bio-age-card.older .bio-age-label {
    color: #dc2626;
}

/* Pace indicator */
.pace-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.8rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.8rem;
}
.pace-slow {
    background: #dcfce7;
    color: #166534;
}
.pace-normal {
    background: #dbeafe;
    color: #1e40af;
}
.pace-fast {
    background: #fee2e2;
    color: #991b1b;
}

/* Pace visual indicator */
.pace-visual {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    margin: 0.5rem 0;
}
.pace-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #e5e7eb;
}
.pace-dot.active { background: #6366f1; }
.pace-dot.slow { background: #22c55e; }
.pace-dot.fast { background: #ef4444; }

/* Welcome page */
.welcome-hero {
    text-align: center;
    padding: 3rem 0;
}
.welcome-logo {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 24px;
    margin: 0 auto 1.5rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.3);
}
.welcome-logo::after {
    content: '';
    width: 32px;
    height: 32px;
    border: 4px solid white;
    border-radius: 50%;
}
.welcome-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}
.welcome-subtitle {
    font-size: 1.1rem;
    color: #6b7280;
    max-width: 500px;
    margin: 0 auto 2rem auto;
    line-height: 1.6;
}

/* Feature cards */
.feature-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 2rem 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(0, 0, 0, 0.04);
    height: 100%;
}
.feature-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    margin: 0 auto 1rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}
.feature-icon.systems {
    background: linear-gradient(135deg, #dbeafe, #bfdbfe);
}
.feature-icon.systems::after {
    content: '';
    display: grid;
    grid-template-columns: repeat(2, 8px);
    grid-template-rows: repeat(2, 8px);
    gap: 4px;
}
.feature-icon.systems::before,
.feature-icon.systems::after {
    content: '';
    position: absolute;
}
.feature-icon.age {
    background: linear-gradient(135deg, #dcfce7, #bbf7d0);
}
.feature-icon.age::after {
    content: '';
    width: 24px;
    height: 24px;
    border: 3px solid #22c55e;
    border-radius: 50%;
}
.feature-icon.pace {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
}
.feature-icon.pace::after {
    content: '';
    width: 0;
    height: 0;
    border-left: 12px solid #f59e0b;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
}
.feature-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}
.feature-desc {
    font-size: 0.85rem;
    color: #6b7280;
    line-height: 1.5;
}

/* Delta indicator */
.delta-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    margin-top: 1rem;
}
.delta-value {
    font-size: 1rem;
    font-weight: 700;
}
.delta-label {
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 0.25rem;
}
.delta-positive { color: #22c55e; }
.delta-negative { color: #ef4444; }
.delta-neutral { color: #6b7280; }

/* Grid dots for systems icon */
.grid-dots {
    display: grid;
    grid-template-columns: repeat(2, 6px);
    gap: 3px;
}
.grid-dots span {
    width: 6px;
    height: 6px;
    background: #3b82f6;
    border-radius: 2px;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE
# =============================================================================

if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'labs' not in st.session_state:
    st.session_state.labs = {}
if 'age' not in st.session_state:
    st.session_state.age = 35
if 'results' not in st.session_state:
    st.session_state.results = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_score_color(score):
    if score >= 80: return '#22c55e'
    if score >= 60: return '#84cc16'
    if score >= 40: return '#f59e0b'
    return '#ef4444'

def get_score_class(score):
    if score >= 80: return 'optimal'
    if score >= 60: return 'good'
    if score >= 40: return 'fair'
    return 'risk'

def get_system_icon_class(system_id):
    icons = {
        'cardiovascular': 'icon-heart',
        'metabolic': 'icon-metabolic',
        'immune': 'icon-immune',
        'blood': 'icon-blood',
        'brain': 'icon-brain',
        'liver': 'icon-liver',
        'kidney': 'icon-kidney',
        'hormonal': 'icon-hormone',
    }
    return icons.get(system_id, 'icon-metabolic')

def create_score_gauge(score, size=200):
    """Create a circular gauge chart with gradient."""
    color = get_score_color(score)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'font': {'size': 52, 'color': '#1a1a2e', 'family': 'Nunito'}, 'suffix': ''},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'tickcolor': 'rgba(0,0,0,0)', 'visible': False},
            'bar': {'color': color, 'thickness': 0.25},
            'bgcolor': '#f3f4f6',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': '#fee2e2'},
                {'range': [40, 60], 'color': '#fef3c7'},
                {'range': [60, 80], 'color': '#ecfccb'},
                {'range': [80, 100], 'color': '#dcfce7'},
            ],
        }
    ))
    
    fig.update_layout(
        height=size,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Nunito', 'color': '#1a1a2e'}
    )
    return fig


# =============================================================================
# PAGES
# =============================================================================

def render_welcome():
    """Welcome/onboarding page."""
    st.markdown("""
    <div class="welcome-hero">
        <div class="welcome-logo"></div>
        <div class="welcome-title">aevum</div>
        <div class="welcome-subtitle">
            Your personal longevity companion. Upload your blood work and discover your biological age, health scores, and personalized insights.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon systems">
                <div class="grid-dots">
                    <span></span><span></span><span></span><span></span>
                </div>
            </div>
            <div class="feature-title">8 Health Systems</div>
            <div class="feature-desc">Comprehensive analysis of cardiovascular, metabolic, immune, and more</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon age"></div>
            <div class="feature-title">Biological Age</div>
            <div class="feature-desc">PhenoAge algorithm calculates your true biological age</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon pace"></div>
            <div class="feature-title">Pace of Aging</div>
            <div class="feature-desc">Are you aging faster or slower than average?</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started", use_container_width=True):
            st.session_state.page = 'upload'
            st.rerun()


def render_upload():
    """Data upload page."""
    st.markdown("""
    <div class="main-title">
        <div class="brand-mark"></div>
        Upload Your Data
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sub-title">We support PDF and CSV blood test results</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="section-header"><span class="section-dot"></span> Your Information</div>', unsafe_allow_html=True)
        
        st.markdown("**Age**")
        st.session_state.age = st.slider(
            "Your age",
            min_value=18,
            max_value=100,
            value=st.session_state.age,
            label_visibility="collapsed"
        )
        st.caption(f"Selected: {st.session_state.age} years old")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-header"><span class="section-dot"></span> Blood Test Results</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload blood test",
            type=['csv', 'pdf'],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.lower().endswith('.pdf'):
                    df = pdf_to_dataframe(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
                
                if len(df) > 0:
                    if 'date' in df.columns:
                        labs_row = df.iloc[-1].drop('date').to_dict()
                    else:
                        labs_row = df.iloc[-1].to_dict()
                    
                    st.session_state.labs = {
                        k: v for k, v in labs_row.items() 
                        if v is not None and not (isinstance(v, float) and pd.isna(v))
                    }
                    
                    if st.session_state.labs:
                        st.markdown(f"""
                        <div class="upload-success">
                            Loaded <strong>{len(st.session_state.labs)}</strong> biomarkers from {uploaded_file.name}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="upload-error">
                            No biomarkers found. Try manual entry.
                        </div>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.markdown(f"""
                <div class="upload-error">
                    Error: {str(e)[:100]}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Use Sample Data"):
            sample_df = create_sample_blood_data()
            labs_row = sample_df.iloc[-1].drop('date').to_dict()
            st.session_state.labs = {k: v for k, v in labs_row.items() if v is not None}
            st.rerun()
    
    with col2:
        st.markdown('<div class="section-header"><span class="section-dot"></span> Manual Entry</div>', unsafe_allow_html=True)
        
        with st.expander("Enter biomarkers manually", expanded=not bool(st.session_state.labs)):
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("**Metabolic**")
                glucose = st.number_input("Glucose (mg/dL)", 0.0, 500.0, 0.0, key="m_glucose")
                if glucose > 0: st.session_state.labs['Glucose'] = glucose
                
                hba1c = st.number_input("HbA1c (%)", 0.0, 15.0, 0.0, key="m_hba1c")
                if hba1c > 0: st.session_state.labs['HbA1c'] = hba1c
                
                st.markdown("**Lipids**")
                ldl = st.number_input("LDL (mg/dL)", 0.0, 300.0, 0.0, key="m_ldl")
                if ldl > 0: st.session_state.labs['LDL'] = ldl
                
                hdl = st.number_input("HDL (mg/dL)", 0.0, 150.0, 0.0, key="m_hdl")
                if hdl > 0: st.session_state.labs['HDL'] = hdl
            
            with c2:
                st.markdown("**Inflammation**")
                crp = st.number_input("hs-CRP (mg/L)", 0.0, 50.0, 0.0, key="m_crp")
                if crp > 0: st.session_state.labs['hs_CRP'] = crp
                
                st.markdown("**Liver**")
                alt = st.number_input("ALT (U/L)", 0.0, 200.0, 0.0, key="m_alt")
                if alt > 0: st.session_state.labs['ALT'] = alt
                
                st.markdown("**Kidney**")
                creat = st.number_input("Creatinine (mg/dL)", 0.0, 10.0, 0.0, key="m_creat")
                if creat > 0: st.session_state.labs['Creatinine'] = creat
                
                albumin = st.number_input("Albumin (g/dL)", 0.0, 6.0, 0.0, key="m_albumin")
                if albumin > 0: st.session_state.labs['Albumin'] = albumin
        
        if st.session_state.labs:
            st.markdown('<div class="section-header"><span class="section-dot"></span> Loaded Biomarkers</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="upload-info">
                {len(st.session_state.labs)} biomarkers ready for analysis
            </div>
            """, unsafe_allow_html=True)
            
            labs_df = pd.DataFrame([
                {"Biomarker": k, "Value": round(v, 2) if isinstance(v, float) else v} 
                for k, v in st.session_state.labs.items()
            ])
            st.dataframe(labs_df, use_container_width=True, hide_index=True, height=200)
    
    st.markdown("---")
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("Back"):
            st.session_state.page = 'welcome'
            st.rerun()
    with c3:
        can_analyze = len(st.session_state.labs) > 0
        if st.button("Analyze", disabled=not can_analyze, use_container_width=True):
            st.session_state.results = run_titan_engine(
                st.session_state.labs,
                st.session_state.age
            )
            st.session_state.page = 'dashboard'
            st.rerun()


def render_dashboard():
    """Main dashboard with results."""
    results = st.session_state.results
    if not results:
        st.session_state.page = 'upload'
        st.rerun()
        return
    
    summary = results['summary']
    systems = results['systems']
    
    st.markdown("""
    <div class="main-title">
        <div class="brand-mark"></div>
        Your Health Report
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Powered by Titan Protocol & PhenoAge Algorithm</div>', unsafe_allow_html=True)
    
    # Top row
    col1, col2, col3 = st.columns([1.2, 1, 1])
    
    with col1:
        st.markdown('<div class="card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Health Score</div>', unsafe_allow_html=True)
        
        score = summary['overall_health_score']
        fig = create_score_gauge(score, size=220)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        score_class = get_score_class(score)
        st.markdown(f'<div class="status-{score_class}" style="margin-top: -15px;">{score_class.title()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        bio_age = summary['bio_age']
        chrono_age = summary['chrono_age']
        age_delta = bio_age - chrono_age
        card_class = "older" if age_delta > 2 else ""
        
        st.markdown(f"""
        <div class="bio-age-card {card_class}">
            <div class="bio-age-label">Biological Age</div>
            <div class="bio-age-value">{bio_age:.0f}</div>
            <div class="card-subtitle">Actual: {chrono_age} years</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Delta
        if age_delta < -1:
            delta_class = "delta-positive"
            delta_text = f"{abs(age_delta):.1f} years younger"
        elif age_delta > 1:
            delta_class = "delta-negative"
            delta_text = f"{age_delta:.1f} years older"
        else:
            delta_class = "delta-neutral"
            delta_text = "On track"
        
        st.markdown(f"""
        <div class="delta-card">
            <div class="delta-value {delta_class}">{delta_text}</div>
            <div class="delta-label">vs actual age</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pace = summary['pace_of_aging']
        if pace < 0.95:
            pace_class = "pace-slow"
            pace_text = "Slower"
        elif pace > 1.05:
            pace_class = "pace-fast"
            pace_text = "Faster"
        else:
            pace_class = "pace-normal"
            pace_text = "Average"
        
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div class="card-title">Pace of Aging</div>
            <div class="pace-visual">
                <div class="pace-dot {'slow' if pace < 0.95 else ''}"></div>
                <div class="pace-dot {'active' if 0.95 <= pace <= 1.05 else ''}"></div>
                <div class="pace-dot {'fast' if pace > 1.05 else ''}"></div>
            </div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #1a1a2e; margin: 0.5rem 0;">{pace:.2f}x</div>
            <div class="pace-badge {pace_class}">{pace_text} than average</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Systems
    st.markdown('<div class="section-header"><span class="section-dot"></span> Your Body Systems</div>', unsafe_allow_html=True)
    
    sorted_systems = sorted(systems, key=lambda x: x['score'])
    
    for row_start in range(0, len(sorted_systems), 4):
        cols = st.columns(4)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(sorted_systems):
                system = sorted_systems[idx]
                score = system['score']
                score_class = get_score_class(score)
                color = get_score_color(score)
                icon_class = get_system_icon_class(system['system_id'])
                
                with col:
                    st.markdown(f"""
                    <div class="system-card">
                        <div class="system-icon {icon_class}"></div>
                        <div class="system-name">{system['name']}</div>
                        <div class="system-score" style="color: {color};">{score:.0f}</div>
                        <div class="system-status">
                            <span class="status-{score_class}">{system['status']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Insights
    st.markdown('<div class="section-header"><span class="section-dot"></span> Key Insights</div>', unsafe_allow_html=True)
    
    insights = results.get('insights', [])
    
    col1, col2 = st.columns(2)
    for idx, insight in enumerate(insights[:6]):
        if "Attention" in insight or "Priority" in insight:
            card_class = "warning"
            icon_class = "warning"
        elif "Excellent" in insight or "Strong" in insight:
            card_class = "success"
            icon_class = "success"
        else:
            card_class = ""
            icon_class = "info"
        
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.markdown(f"""
            <div class="insight-card {card_class}">
                <div class="insight-icon {icon_class}"></div>
                <div>{insight}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Biomarkers
    with st.expander("View All Biomarkers"):
        all_markers = []
        for system in systems:
            for marker in system.get('markers_used', []):
                all_markers.append({
                    'System': system['name'],
                    'Marker': marker['id'],
                    'Value': round(marker['value'], 2),
                    'Score': round(marker['score'], 0)
                })
        
        if all_markers:
            df = pd.DataFrame(all_markers)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("New Analysis"):
            st.session_state.page = 'upload'
            st.session_state.labs = {}
            st.session_state.results = None
            st.rerun()


# =============================================================================
# MAIN
# =============================================================================

def main():
    if st.session_state.page == 'welcome':
        render_welcome()
    elif st.session_state.page == 'upload':
        render_upload()
    elif st.session_state.page == 'dashboard':
        render_dashboard()
    else:
        render_welcome()


if __name__ == "__main__":
    main()
