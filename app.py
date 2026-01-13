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

# Light theme with Nunito font
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
    max-width: 1200px; 
}

/* Typography */
h1, h2, h3 {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: #1a1a2e !important;
}

.main-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.sub-title {
    font-size: 0.95rem;
    color: #6b7280;
    margin-bottom: 2rem;
    font-weight: 500;
}

/* Logo/Brand mark */
.brand-mark {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: relative;
}
.brand-mark::before {
    content: '';
    width: 14px;
    height: 14px;
    border: 2px solid white;
    border-radius: 50%;
}
.brand-mark::after {
    content: '';
    position: absolute;
    width: 5px;
    height: 5px;
    background: white;
    border-radius: 50%;
}

/* Cards */
.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    margin-bottom: 1rem;
    border: 1px solid rgba(0, 0, 0, 0.04);
}
.card-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
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

/* System cards - matching reference design */
.system-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(0, 0, 0, 0.04);
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
}
.system-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}
.system-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
}
.system-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    border: 1.5px solid #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    position: relative;
}
/* CSS-only icons */
.icon-heart::before {
    content: '';
    width: 18px;
    height: 16px;
    background: transparent;
    border: 2px solid #374151;
    border-radius: 50% 50% 0 0;
    transform: rotate(-45deg);
    position: relative;
    top: -2px;
}
.icon-lightning::before {
    content: '';
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-bottom: 16px solid #374151;
}
.icon-shield::before {
    content: '';
    width: 14px;
    height: 16px;
    border: 2px solid #374151;
    border-radius: 2px 2px 8px 8px;
}
.icon-droplet::before {
    content: '';
    width: 12px;
    height: 16px;
    border: 2px solid #374151;
    border-radius: 50% 50% 50% 50% / 30% 30% 70% 70%;
}
.icon-brain::before {
    content: '';
    width: 16px;
    height: 16px;
    border: 2px solid #374151;
    border-radius: 50%;
}
.icon-liver::before {
    content: '';
    width: 18px;
    height: 12px;
    border: 2px solid #374151;
    border-radius: 3px;
}
.icon-kidney::before {
    content: '';
    width: 14px;
    height: 14px;
    border: 2px solid #374151;
    border-radius: 50%;
}
.icon-kidney::after {
    content: '';
    position: absolute;
    width: 6px;
    height: 6px;
    background: #374151;
    border-radius: 50%;
}
.icon-hormone::before {
    content: '';
    width: 14px;
    height: 14px;
    border: 2px solid #374151;
    border-radius: 50%;
}
.icon-hormone::after {
    content: '';
    position: absolute;
    width: 6px;
    height: 6px;
    background: #374151;
    border-radius: 50%;
}
.alert-badge {
    background: #fee2e2;
    color: #dc2626;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.25rem 0.6rem;
    border-radius: 12px;
}
.system-name {
    font-size: 1rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.75rem;
}
.system-score-row {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}
.system-score {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
}
.system-score-max {
    font-size: 1rem;
    font-weight: 600;
    color: #9ca3af;
}
.system-biomarker-count {
    font-size: 0.8rem;
    color: #9ca3af;
    font-weight: 500;
}
.system-progress {
    height: 6px;
    background: #f3f4f6;
    border-radius: 3px;
    margin: 0.75rem 0;
    overflow: hidden;
}
.system-progress-bar {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s;
}
.system-status {
    font-size: 0.85rem;
    font-weight: 700;
}

/* Status colors */
.status-optimal { color: #22c55e; }
.status-good { color: #84cc16; }
.status-moderate { color: #f59e0b; }
.status-critical { color: #ef4444; }
.bg-optimal { background: linear-gradient(90deg, #22c55e, #4ade80); }
.bg-good { background: linear-gradient(90deg, #84cc16, #a3e635); }
.bg-moderate { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.bg-critical { background: linear-gradient(90deg, #ef4444, #f87171); }

/* Score colors */
.score-optimal { color: #22c55e; }
.score-good { color: #84cc16; }
.score-moderate { color: #f59e0b; }
.score-critical { color: #ef4444; }

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 2rem 0 1rem 0;
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

/* Buttons - remove all emojis/icons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
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

/* File uploader - clean styling */
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
.stSlider label { color: #374151 !important; font-weight: 600 !important; }

/* Number input */
.stNumberInput input {
    background: #ffffff !important;
    border: 2px solid #e5e7eb !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    color: #1a1a2e !important;
}
.stNumberInput label { color: #374151 !important; font-weight: 600 !important; }

/* Expander - light theme */
.stExpander {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
}
.stExpander > details > summary {
    background: #ffffff !important;
    color: #1a1a2e !important;
    font-weight: 600 !important;
    font-family: 'Nunito', sans-serif !important;
}
.stExpander > details > summary:hover {
    background: #f9fafb !important;
}
.stExpander > details[open] > summary {
    border-bottom: 1px solid #e5e7eb !important;
}

/* Dataframe - light theme */
.stDataFrame {
    background: #ffffff !important;
}
.stDataFrame > div {
    background: #ffffff !important;
}
[data-testid="stDataFrame"] > div {
    background: #ffffff !important;
}
[data-testid="stDataFrame"] iframe {
    background: #ffffff !important;
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
    gap: 0.75rem;
}
.success-dot {
    width: 8px;
    height: 8px;
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
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    border: 2px solid #dcfce7;
}
.bio-age-value {
    font-size: 3rem;
    font-weight: 800;
    color: #166534;
    line-height: 1;
}
.bio-age-label {
    font-size: 0.7rem;
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

/* Pace indicator - clean */
.pace-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: #1a1a2e;
    line-height: 1;
}
.pace-badge {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.75rem;
    margin-top: 0.5rem;
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

/* Welcome page */
.welcome-hero {
    text-align: center;
    padding: 3rem 0;
}
.welcome-logo {
    width: 72px;
    height: 72px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 20px;
    margin: 0 auto 1.5rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.3);
    position: relative;
}
.welcome-logo::before {
    content: '';
    width: 28px;
    height: 28px;
    border: 3px solid white;
    border-radius: 50%;
}
.welcome-logo::after {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
    background: white;
    border-radius: 50%;
}
.welcome-title {
    font-size: 2.25rem;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}
.welcome-subtitle {
    font-size: 1rem;
    color: #6b7280;
    max-width: 500px;
    margin: 0 auto 2rem auto;
    line-height: 1.6;
}

/* Feature cards */
.feature-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(0, 0, 0, 0.04);
    height: 100%;
}
.feature-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    margin: 0 auto 1rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}
.feature-icon.systems {
    background: linear-gradient(135deg, #dbeafe, #bfdbfe);
}
.feature-icon.systems::before {
    content: '';
    display: grid;
    grid-template-columns: repeat(2, 8px);
    grid-template-rows: repeat(2, 8px);
    gap: 4px;
}
.feature-icon.systems::before {
    content: '';
    width: 8px;
    height: 8px;
    background: #3b82f6;
    border-radius: 2px;
    box-shadow: 12px 0 0 #3b82f6, 0 12px 0 #3b82f6, 12px 12px 0 #3b82f6;
}
.feature-icon.age {
    background: linear-gradient(135deg, #dcfce7, #bbf7d0);
}
.feature-icon.age::before {
    content: '';
    width: 20px;
    height: 20px;
    border: 2.5px solid #22c55e;
    border-radius: 50%;
}
.feature-icon.age::after {
    content: '';
    position: absolute;
    width: 2.5px;
    height: 8px;
    background: #22c55e;
    top: 14px;
    transform-origin: bottom;
    transform: rotate(45deg);
}
.feature-icon.pace {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
}
.feature-icon.pace::before {
    content: '';
    width: 0;
    height: 0;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
    border-left: 14px solid #f59e0b;
    margin-left: 4px;
}
.feature-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}
.feature-desc {
    font-size: 0.8rem;
    color: #6b7280;
    line-height: 1.5;
}

/* Delta indicator */
.delta-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 0.75rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    margin-top: 0.75rem;
}
.delta-value {
    font-size: 0.9rem;
    font-weight: 700;
}
.delta-label {
    font-size: 0.7rem;
    color: #9ca3af;
    margin-top: 0.15rem;
}
.delta-positive { color: #22c55e; }
.delta-negative { color: #ef4444; }
.delta-neutral { color: #6b7280; }

/* Custom table styling */
.biomarker-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}
.biomarker-table th {
    text-align: left;
    padding: 0.75rem 1rem;
    background: #f9fafb;
    color: #6b7280;
    font-weight: 600;
    border-bottom: 1px solid #e5e7eb;
}
.biomarker-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #f3f4f6;
    color: #374151;
}
.biomarker-table tr:hover {
    background: #f9fafb;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SVG ICONS
# =============================================================================

# System icon class mapping (CSS-only icons)

SYSTEM_ICONS = {
    'cardiovascular': 'heart',
    'metabolic': 'lightning',
    'immune': 'shield',
    'blood': 'droplet',
    'brain': 'brain',
    'liver': 'liver',
    'kidney': 'kidney',
    'hormonal': 'hormone',
}


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
    if score >= 40: return 'moderate'
    return 'critical'

def get_status_label(score):
    if score >= 80: return 'Optimal'
    if score >= 60: return 'Good'
    if score >= 40: return 'Moderate'
    return 'Critical'

def create_score_gauge(score, size=200):
    """Create a circular gauge chart with gradient."""
    color = get_score_color(score)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'font': {'size': 48, 'color': '#1a1a2e', 'family': 'Nunito'}, 'suffix': ''},
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


def render_system_card(system):
    """Render a system card matching the reference design."""
    score = system['score']
    status = get_status_label(score)
    status_class = get_score_class(score)
    icon_name = SYSTEM_ICONS.get(system['system_id'], 'brain')
    icon_class = f"icon-{icon_name}"
    markers_count = len(system.get('markers_used', []))
    
    # Count alerts (markers with score < 60)
    alerts = sum(1 for m in system.get('markers_used', []) if m.get('score', 100) < 60)
    alert_html = f'<span class="alert-badge">{alerts} Alerts</span>' if alerts > 0 else ''
    
    return f"""<div class="system-card"><div class="system-header"><div class="system-icon {icon_class}"></div>{alert_html}</div><div class="system-name">{system['name']}</div><div class="system-score-row"><span class="system-score score-{status_class}">{score:.0f}</span><span class="system-score-max">/100</span><span class="system-biomarker-count">{markers_count} Biomarkers</span></div><div class="system-progress"><div class="system-progress-bar bg-{status_class}" style="width: {score}%;"></div></div><div class="system-status status-{status_class}">{status}</div></div>"""


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
            <div class="feature-icon systems"></div>
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
        st.markdown('<div class="section-header">Your Information</div>', unsafe_allow_html=True)
        
        st.session_state.age = st.slider(
            "Age",
            min_value=18,
            max_value=100,
            value=st.session_state.age,
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">Blood Test Results</div>', unsafe_allow_html=True)
        
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
                            <span class="success-dot"></span>
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
        st.markdown('<div class="section-header">Manual Entry</div>', unsafe_allow_html=True)
        
        with st.expander("Enter biomarkers manually", expanded=not bool(st.session_state.labs)):
            c1, c2 = st.columns(2)
            
            with c1:
                glucose = st.number_input("Glucose (mg/dL)", 0.0, 500.0, 0.0, key="m_glucose")
                if glucose > 0: st.session_state.labs['Glucose'] = glucose
                
                hba1c = st.number_input("HbA1c (%)", 0.0, 15.0, 0.0, key="m_hba1c")
                if hba1c > 0: st.session_state.labs['HbA1c'] = hba1c
                
                ldl = st.number_input("LDL (mg/dL)", 0.0, 300.0, 0.0, key="m_ldl")
                if ldl > 0: st.session_state.labs['LDL'] = ldl
                
                hdl = st.number_input("HDL (mg/dL)", 0.0, 150.0, 0.0, key="m_hdl")
                if hdl > 0: st.session_state.labs['HDL'] = hdl
            
            with c2:
                crp = st.number_input("hs-CRP (mg/L)", 0.0, 50.0, 0.0, key="m_crp")
                if crp > 0: st.session_state.labs['hs_CRP'] = crp
                
                alt = st.number_input("ALT (U/L)", 0.0, 200.0, 0.0, key="m_alt")
                if alt > 0: st.session_state.labs['ALT'] = alt
                
                creat = st.number_input("Creatinine (mg/dL)", 0.0, 10.0, 0.0, key="m_creat")
                if creat > 0: st.session_state.labs['Creatinine'] = creat
                
                albumin = st.number_input("Albumin (g/dL)", 0.0, 6.0, 0.0, key="m_albumin")
                if albumin > 0: st.session_state.labs['Albumin'] = albumin
        
        if st.session_state.labs:
            st.markdown('<div class="section-header">Loaded Biomarkers</div>', unsafe_allow_html=True)
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
    
    c1, c2, c3 = st.columns([1, 2, 1])
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
        fig = create_score_gauge(score, size=200)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        status = get_status_label(score)
        status_class = get_score_class(score)
        st.markdown(f'<div class="system-status status-{status_class}" style="margin-top: -15px;">{status}</div>', unsafe_allow_html=True)
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
            <div class="card-subtitle">Chronological: {chrono_age} years</div>
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
            <div class="delta-label">vs chronological age</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Pace of aging = bio_age / chrono_age
        bio_age = summary['bio_age']
        chrono_age = summary['chrono_age']
        pace = bio_age / chrono_age if chrono_age > 0 else 1.0
        
        if pace < 0.95:
            pace_class = "pace-slow"
            pace_text = "Slower than average"
        elif pace > 1.05:
            pace_class = "pace-fast"
            pace_text = "Faster than average"
        else:
            pace_class = "pace-normal"
            pace_text = "Average"
        
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div class="card-title">Pace of Aging</div>
            <div class="pace-value">{pace:.2f}x</div>
            <div class="card-subtitle">Bio Age / Chrono Age</div>
            <div class="pace-badge {pace_class}">{pace_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Systems
    st.markdown('<div class="section-header">Your Body Systems</div>', unsafe_allow_html=True)
    
    sorted_systems = sorted(systems, key=lambda x: x['score'])
    
    for row_start in range(0, len(sorted_systems), 4):
        cols = st.columns(4)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(sorted_systems):
                system = sorted_systems[idx]
                with col:
                    st.markdown(render_system_card(system), unsafe_allow_html=True)
    
    # Insights
    st.markdown('<div class="section-header">Key Insights</div>', unsafe_allow_html=True)
    
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
                    'Score': int(round(marker['score'], 0))
                })
        
        if all_markers:
            df = pd.DataFrame(all_markers)
            st.dataframe(df, use_container_width=True, hide_index=True, height=400)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
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
