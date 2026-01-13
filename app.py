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
    page_icon="🧬",
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
}
.sub-title {
    font-size: 1rem;
    color: #6b7280;
    margin-bottom: 2rem;
    font-weight: 500;
}

/* Cards - Light theme */
.card {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    margin-bottom: 1rem;
    border: 1px solid rgba(0, 0, 0, 0.04);
}
.card-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #6b7280;
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
    font-size: 0.9rem;
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
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    margin-bottom: 0.75rem;
}
.system-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.25rem;
}
.system-score {
    font-size: 1.75rem;
    font-weight: 800;
}
.system-status {
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.25rem;
}

/* Status badge colors */
.status-optimal { 
    color: #22c55e; 
    background: #dcfce7;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    display: inline-block;
}
.status-good { 
    color: #65a30d; 
    background: #ecfccb;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    display: inline-block;
}
.status-fair { 
    color: #d97706; 
    background: #fef3c7;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    display: inline-block;
}
.status-risk { 
    color: #dc2626; 
    background: #fee2e2;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    display: inline-block;
}

/* Icon backgrounds */
.icon-heart { background: linear-gradient(135deg, #fee2e2, #fecaca); }
.icon-metabolic { background: linear-gradient(135deg, #dbeafe, #bfdbfe); }
.icon-immune { background: linear-gradient(135deg, #dcfce7, #bbf7d0); }
.icon-blood { background: linear-gradient(135deg, #fce7f3, #fbcfe8); }
.icon-brain { background: linear-gradient(135deg, #e0e7ff, #c7d2fe); }
.icon-liver { background: linear-gradient(135deg, #fef3c7, #fde68a); }
.icon-kidney { background: linear-gradient(135deg, #ccfbf1, #99f6e4); }
.icon-hormone { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); }

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Insights */
.insight-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    border-left: 4px solid #3b82f6;
    font-size: 0.9rem;
    color: #374151;
}
.insight-card.warning {
    border-left-color: #f59e0b;
    background: #fffbeb;
}
.insight-card.success {
    border-left-color: #22c55e;
    background: #f0fdf4;
}

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
.stNumberInput input:focus {
    border-color: #6366f1 !important;
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

/* Expander */
.streamlit-expanderHeader {
    background: #ffffff !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 600 !important;
}

/* Data table */
.stDataFrame {
    background: #ffffff;
    border-radius: 12px;
}

/* Messages */
.upload-success {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    color: #166534;
    font-weight: 600;
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
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
    border: 1px solid #86efac;
}
.bio-age-value {
    font-size: 3rem;
    font-weight: 800;
    color: #166534;
}
.bio-age-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #22c55e;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.bio-age-card.older {
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
    border-color: #fca5a5;
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
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-weight: 700;
    font-size: 0.9rem;
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
.welcome-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
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

/* Feature cards on welcome */
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
    font-size: 2.5rem;
    margin-bottom: 1rem;
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

def get_system_icon(system_id):
    icons = {
        'cardiovascular': ('❤️', 'icon-heart'),
        'metabolic': ('🔥', 'icon-metabolic'),
        'immune': ('🛡️', 'icon-immune'),
        'blood': ('🩸', 'icon-blood'),
        'brain': ('🧠', 'icon-brain'),
        'liver': ('🫀', 'icon-liver'),
        'kidney': ('💧', 'icon-kidney'),
        'hormonal': ('⚡', 'icon-hormone'),
    }
    return icons.get(system_id, ('📊', 'icon-metabolic'))

def create_score_gauge(score, size=200):
    """Create a circular gauge chart with gradient."""
    color = get_score_color(score)
    
    # Create the gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'font': {'size': 48, 'color': '#1a1a2e', 'family': 'Nunito'}, 'suffix': ''},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'tickcolor': 'rgba(0,0,0,0)', 'visible': False},
            'bar': {'color': color, 'thickness': 0.3},
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
        <div class="welcome-icon">🧬</div>
        <div class="welcome-title">aevum</div>
        <div class="welcome-subtitle">
            Your personal longevity companion. Upload your blood work and discover your biological age, health scores, and personalized insights.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">8 Health Systems</div>
            <div class="feature-desc">Comprehensive analysis of cardiovascular, metabolic, immune, and more</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Biological Age</div>
            <div class="feature-desc">PhenoAge algorithm calculates your true biological age</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Pace of Aging</div>
            <div class="feature-desc">Are you aging faster or slower than average?</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started →", use_container_width=True):
            st.session_state.page = 'upload'
            st.rerun()


def render_upload():
    """Data upload page."""
    st.markdown('<div class="main-title">📋 Upload Your Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">We support PDF and CSV blood test results</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="section-header">👤 Your Information</div>', unsafe_allow_html=True)
        
        # Age slider
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
        
        # File upload
        st.markdown('<div class="section-header">📄 Blood Test Results</div>', unsafe_allow_html=True)
        
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
                            ✓ Loaded <strong>{len(st.session_state.labs)}</strong> biomarkers from {uploaded_file.name}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="upload-error">
                            ⚠️ No biomarkers found. Try manual entry.
                        </div>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.markdown(f"""
                <div class="upload-error">
                    ⚠️ Error: {str(e)[:100]}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧪 Use Sample Data"):
            sample_df = create_sample_blood_data()
            labs_row = sample_df.iloc[-1].drop('date').to_dict()
            st.session_state.labs = {k: v for k, v in labs_row.items() if v is not None}
            st.rerun()
    
    with col2:
        st.markdown('<div class="section-header">✏️ Manual Entry</div>', unsafe_allow_html=True)
        
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
            st.markdown('<div class="section-header">📊 Loaded Biomarkers</div>', unsafe_allow_html=True)
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
        if st.button("← Back"):
            st.session_state.page = 'welcome'
            st.rerun()
    with c3:
        can_analyze = len(st.session_state.labs) > 0
        if st.button("Analyze →", disabled=not can_analyze, use_container_width=True):
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
    
    # Header
    st.markdown('<div class="main-title">🧬 Your Health Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Powered by Titan Protocol & PhenoAge Algorithm</div>', unsafe_allow_html=True)
    
    # Top row - Score + Bio Age + Pace
    col1, col2, col3 = st.columns([1.2, 1, 1])
    
    with col1:
        st.markdown('<div class="card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Health Score</div>', unsafe_allow_html=True)
        
        score = summary['overall_health_score']
        fig = create_score_gauge(score, size=220)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        score_class = get_score_class(score)
        st.markdown(f'<div class="status-{score_class}" style="margin-top: -20px;">{score_class.title()}</div>', unsafe_allow_html=True)
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
            <div class="card-subtitle" style="color: #6b7280;">Actual: {chrono_age} years</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Age delta
        delta_text = f"{abs(age_delta):.1f} years younger" if age_delta < 0 else f"{age_delta:.1f} years older" if age_delta > 0 else "On track"
        delta_color = "#22c55e" if age_delta < 0 else "#ef4444" if age_delta > 2 else "#6b7280"
        
        st.markdown(f"""
        <div class="card" style="text-align: center; margin-top: 1rem;">
            <div style="font-size: 1.1rem; font-weight: 700; color: {delta_color};">{delta_text}</div>
            <div style="font-size: 0.8rem; color: #9ca3af;">vs actual age</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pace = summary['pace_of_aging']
        pace_class = "pace-slow" if pace < 0.95 else "pace-fast" if pace > 1.05 else "pace-normal"
        pace_icon = "🐢" if pace < 0.95 else "🐇" if pace > 1.05 else "⚖️"
        pace_text = "Slower" if pace < 0.95 else "Faster" if pace > 1.05 else "Average"
        
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div class="card-title">Pace of Aging</div>
            <div style="font-size: 3rem; margin: 0.5rem 0;">{pace_icon}</div>
            <div style="font-size: 2rem; font-weight: 800; color: #1a1a2e;">{pace:.2f}x</div>
            <div class="pace-badge {pace_class}" style="margin-top: 0.75rem;">{pace_text} than average</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Body Systems Section
    st.markdown('<div class="section-header">🫀 Your Body Systems</div>', unsafe_allow_html=True)
    
    # Sort by score (lowest first to highlight areas needing attention)
    sorted_systems = sorted(systems, key=lambda x: x['score'])
    
    # Display in 2 rows of 4
    for row_start in range(0, len(sorted_systems), 4):
        cols = st.columns(4)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(sorted_systems):
                system = sorted_systems[idx]
                score = system['score']
                score_class = get_score_class(score)
                color = get_score_color(score)
                icon, icon_class = get_system_icon(system['system_id'])
                
                with col:
                    st.markdown(f"""
                    <div class="system-card">
                        <div class="system-icon {icon_class}">{icon}</div>
                        <div class="system-name">{system['name']}</div>
                        <div class="system-score" style="color: {color};">{score:.0f}</div>
                        <div class="system-status">
                            <span class="status-{score_class}">{system['status']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Insights Section
    st.markdown('<div class="section-header">💡 Key Insights</div>', unsafe_allow_html=True)
    
    insights = results.get('insights', [])
    
    col1, col2 = st.columns(2)
    for idx, insight in enumerate(insights[:6]):
        card_class = "warning" if "Attention" in insight or "Priority" in insight else "success" if "Excellent" in insight or "Strong" in insight else ""
        icon = "⚠️" if "warning" in card_class else "✓" if "success" in card_class else "💡"
        
        target_col = col1 if idx % 2 == 0 else col2
        with target_col:
            st.markdown(f"""
            <div class="insight-card {card_class}">
                {icon} {insight}
            </div>
            """, unsafe_allow_html=True)
    
    # Biomarkers Section
    with st.expander("📋 View All Biomarkers"):
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
        if st.button("← New Analysis"):
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
