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
from modules.data_extraction import pdf_to_dataframe, parse_whoop_csv

# =============================================================================
# PAGE CONFIG & STYLES
# =============================================================================

st.set_page_config(
    page_title="Aevum",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, modern CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset & Base */
.stApp { background: #0a0a0a; }
* { font-family: 'Inter', sans-serif; }

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1rem 3rem 1rem; max-width: 500px; margin: 0 auto; }

/* Typography */
.main-title {
    font-size: 2rem;
    font-weight: 700;
    color: #fff;
    text-align: center;
    margin-bottom: 0.25rem;
}
.sub-title {
    font-size: 0.9rem;
    color: #6b7280;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* Score Circle */
.score-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem auto;
    position: relative;
}
.score-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #fff;
}
.score-label {
    font-size: 0.75rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Cards */
.metric-card {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.metric-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}
.metric-card-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #fff;
}
.metric-card-score {
    font-size: 1.5rem;
    font-weight: 700;
}

/* System Cards */
.system-card {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.system-score-ring {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
}
.system-info {
    flex: 1;
}
.system-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #fff;
    margin-bottom: 0.25rem;
}
.system-status {
    font-size: 0.75rem;
    color: #9ca3af;
}
.system-markers {
    font-size: 0.7rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

/* Status colors */
.status-optimal { color: #22c55e; }
.status-good { color: #84cc16; }
.status-fair { color: #f59e0b; }
.status-risk { color: #ef4444; }

.ring-optimal { background: linear-gradient(135deg, #22c55e22, #22c55e44); border: 2px solid #22c55e; }
.ring-good { background: linear-gradient(135deg, #84cc1622, #84cc1644); border: 2px solid #84cc16; }
.ring-fair { background: linear-gradient(135deg, #f59e0b22, #f59e0b44); border: 2px solid #f59e0b; }
.ring-risk { background: linear-gradient(135deg, #ef444422, #ef444444); border: 2px solid #ef4444; }

/* Insights */
.insight-item {
    background: #1a1a1a;
    border-left: 3px solid #3b82f6;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.85rem;
    color: #d1d5db;
}

/* Upload area */
.upload-area {
    background: #141414;
    border: 2px dashed #2a2a2a;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1rem;
}
.upload-area:hover {
    border-color: #3b82f6;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
}

/* Age pills */
.age-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #1a1a1a;
    border-radius: 20px;
    padding: 0.5rem 1rem;
    margin: 0.25rem;
}
.age-pill-value {
    font-size: 1.25rem;
    font-weight: 700;
}
.age-pill-label {
    font-size: 0.7rem;
    color: #9ca3af;
    text-transform: uppercase;
}

/* Pace indicator */
.pace-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 12px;
    margin: 0.5rem auto;
    width: fit-content;
}
.pace-slow { background: #22c55e22; color: #22c55e; }
.pace-normal { background: #3b82f622; color: #3b82f6; }
.pace-fast { background: #ef444422; color: #ef4444; }

/* Hide file uploader label */
.stFileUploader > label { display: none; }
.uploadedFile { display: none; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #141414;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #9ca3af;
    padding: 0.5rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: #2a2a2a;
    color: #fff;
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

def get_status_class(status):
    return f"status-{status.lower()}"

def get_ring_class(status):
    return f"ring-{status.lower()}"

def create_gauge_chart(value, title=""):
    """Create a circular gauge chart."""
    color = get_score_color(value)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': '', 'font': {'size': 40, 'color': '#fff'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 0, 'tickcolor': 'rgba(0,0,0,0)'},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': '#1a1a1a',
            'borderwidth': 0,
            'steps': [{'range': [0, 100], 'color': '#1a1a1a'}],
            'threshold': {
                'line': {'color': color, 'width': 0},
                'thickness': 0,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#fff'}
    )
    return fig


# =============================================================================
# PAGES
# =============================================================================

def render_welcome():
    """Welcome/onboarding page."""
    st.markdown('<div class="main-title">aevum</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Your longevity analytics companion</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🧬</div>
        <p style="color: #9ca3af; font-size: 0.95rem; max-width: 300px; margin: 0 auto 2rem auto;">
            Upload your blood work and get personalized insights into your biological age and health systems.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick info cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
            <div style="font-size: 0.75rem; color: #9ca3af;">8 Health Systems</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎯</div>
            <div style="font-size: 0.75rem; color: #9ca3af;">Bio Age</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚡</div>
            <div style="font-size: 0.75rem; color: #9ca3af;">Pace of Aging</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Get Started →", use_container_width=True):
        st.session_state.page = 'upload'
        st.rerun()


def render_upload():
    """Data upload page."""
    st.markdown('<div class="main-title">Upload Your Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">We support PDF and CSV blood test results</div>', unsafe_allow_html=True)
    
    # Age input
    st.markdown("#### Your Age")
    st.session_state.age = st.number_input("Age", 18, 100, st.session_state.age, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # File upload
    st.markdown("#### Blood Test Results")
    uploaded_file = st.file_uploader("Upload", type=['csv', 'pdf'], label_visibility="collapsed")
    
    if uploaded_file:
        try:
            if uploaded_file.name.lower().endswith('.pdf'):
                df = pdf_to_dataframe(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
            
            if len(df) > 0:
                # Convert to labs dict
                if 'date' in df.columns:
                    labs_row = df.iloc[-1].drop('date').to_dict()
                else:
                    labs_row = df.iloc[-1].to_dict()
                
                st.session_state.labs = {k: v for k, v in labs_row.items() 
                                         if v is not None and not (isinstance(v, float) and pd.isna(v))}
                st.success(f"✓ Loaded {len(st.session_state.labs)} biomarkers")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Manual entry option
    with st.expander("Or enter manually"):
        st.markdown("Enter key biomarkers:")
        
        col1, col2 = st.columns(2)
        with col1:
            glucose = st.number_input("Glucose (mg/dL)", 0.0, 500.0, 0.0)
            if glucose > 0: st.session_state.labs['Glucose'] = glucose
            
            hba1c = st.number_input("HbA1c (%)", 0.0, 15.0, 0.0)
            if hba1c > 0: st.session_state.labs['HbA1c'] = hba1c
            
            crp = st.number_input("hs-CRP (mg/L)", 0.0, 50.0, 0.0)
            if crp > 0: st.session_state.labs['hs_CRP'] = crp
            
            ldl = st.number_input("LDL (mg/dL)", 0.0, 300.0, 0.0)
            if ldl > 0: st.session_state.labs['LDL'] = ldl
        
        with col2:
            hdl = st.number_input("HDL (mg/dL)", 0.0, 150.0, 0.0)
            if hdl > 0: st.session_state.labs['HDL'] = hdl
            
            trig = st.number_input("Triglycerides (mg/dL)", 0.0, 500.0, 0.0)
            if trig > 0: st.session_state.labs['Triglycerides'] = trig
            
            alt = st.number_input("ALT (U/L)", 0.0, 200.0, 0.0)
            if alt > 0: st.session_state.labs['ALT'] = alt
            
            creat = st.number_input("Creatinine (mg/dL)", 0.0, 10.0, 0.0)
            if creat > 0: st.session_state.labs['Creatinine'] = creat
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Show loaded markers count
    if st.session_state.labs:
        st.info(f"📊 {len(st.session_state.labs)} biomarkers ready for analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.page = 'welcome'
            st.rerun()
    with col2:
        if st.button("Analyze →", disabled=len(st.session_state.labs) == 0):
            # Run Titan Engine
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
    st.markdown('<div class="main-title">aevum</div>', unsafe_allow_html=True)
    
    # Overall Score
    score = summary['overall_health_score']
    color = get_score_color(score)
    
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <div class="score-circle" style="background: linear-gradient(135deg, {color}22, {color}44); border: 3px solid {color};">
            <div class="score-value">{score:.0f}</div>
            <div class="score-label">Health Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Age & Pace Pills
    bio_age = summary['bio_age']
    chrono_age = summary['chrono_age']
    pace = summary['pace_of_aging']
    
    age_delta = bio_age - chrono_age
    delta_color = '#22c55e' if age_delta < 0 else '#ef4444' if age_delta > 2 else '#9ca3af'
    delta_text = f"{abs(age_delta):.1f}y younger" if age_delta < 0 else f"{age_delta:.1f}y older" if age_delta > 0 else "on track"
    
    st.markdown(f"""
    <div style="display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
        <div class="age-pill">
            <div>
                <div class="age-pill-value" style="color: {delta_color};">{bio_age:.0f}</div>
                <div class="age-pill-label">Bio Age</div>
            </div>
        </div>
        <div class="age-pill">
            <div>
                <div class="age-pill-value">{chrono_age}</div>
                <div class="age-pill-label">Actual</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pace indicator
    pace_class = 'pace-slow' if pace < 0.95 else 'pace-fast' if pace > 1.05 else 'pace-normal'
    pace_icon = '🐢' if pace < 0.95 else '🐇' if pace > 1.05 else '⚖️'
    
    st.markdown(f"""
    <div class="pace-indicator {pace_class}">
        <span>{pace_icon}</span>
        <span style="font-weight: 600;">Pace: {pace:.2f}x</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Systems", "Insights", "Details"])
    
    with tab1:
        # System Cards
        st.markdown("#### Your Body Systems")
        
        for system in sorted(systems, key=lambda x: x['score']):
            score = system['score']
            status = system['status']
            color = get_score_color(score)
            ring_class = get_ring_class(status)
            status_class = get_status_class(status)
            
            # Top markers
            top_markers = system.get('top_markers', [])[:2]
            markers_text = ", ".join([f"{m['id']}: {m['value']:.1f}" for m in top_markers]) if top_markers else "No data"
            
            st.markdown(f"""
            <div class="system-card">
                <div class="system-score-ring {ring_class}">{score:.0f}</div>
                <div class="system-info">
                    <div class="system-name">{system['name']}</div>
                    <div class="system-status {status_class}">{status}</div>
                    <div class="system-markers">{markers_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        # Insights
        st.markdown("#### Key Insights")
        
        for insight in results.get('insights', []):
            icon = '⚠️' if 'Priority' in insight or 'Attention' in insight else '✓' if 'Excellent' in insight or 'Strong' in insight else '💡'
            st.markdown(f"""
            <div class="insight-item">
                {icon} {insight}
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        # Detailed breakdown
        st.markdown("#### Biomarkers Analyzed")
        st.markdown(f"**{results['labs_processed']}** biomarkers processed")
        
        # Show all markers in a clean format
        all_markers = []
        for system in systems:
            for marker in system.get('markers_used', []):
                all_markers.append({
                    'System': system['name'],
                    'Marker': marker['id'],
                    'Value': marker['value'],
                    'Score': marker['score']
                })
        
        if all_markers:
            df = pd.DataFrame(all_markers)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← New Analysis"):
            st.session_state.page = 'upload'
            st.session_state.labs = {}
            st.session_state.results = None
            st.rerun()
    with col2:
        if st.button("Export JSON"):
            st.json(results)


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
