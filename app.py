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

# Clean, modern CSS - DESKTOP OPTIMIZED
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset & Base */
.stApp { background: #0a0a0a; }
* { font-family: 'Inter', sans-serif; }

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1200px; }

/* Typography */
.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.5rem;
}
.sub-title {
    font-size: 1rem;
    color: #6b7280;
    margin-bottom: 2rem;
}

/* Score Circle - larger for desktop */
.score-circle {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.5rem auto;
}
.score-value {
    font-size: 3.5rem;
    font-weight: 700;
    color: #fff;
}
.score-label {
    font-size: 0.85rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Cards */
.metric-card {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    height: 100%;
}
.metric-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}
.metric-card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #fff;
}

/* System Cards - grid layout for desktop */
.system-card {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 16px;
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    height: 100%;
}
.system-score-ring {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
}
.system-info {
    flex: 1;
}
.system-name {
    font-size: 1rem;
    font-weight: 600;
    color: #fff;
    margin-bottom: 0.25rem;
}
.system-status {
    font-size: 0.8rem;
}
.system-markers {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.35rem;
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
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    color: #d1d5db;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
}
.stButton > button:disabled {
    background: #333 !important;
    color: #666 !important;
}

/* Age pills */
.age-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    background: #1a1a1a;
    border-radius: 20px;
    padding: 0.75rem 1.5rem;
    margin: 0.5rem;
}
.age-pill-value {
    font-size: 1.5rem;
    font-weight: 700;
}
.age-pill-label {
    font-size: 0.75rem;
    color: #9ca3af;
    text-transform: uppercase;
}

/* Pace indicator */
.pace-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    margin: 1rem auto;
    width: fit-content;
    font-size: 1rem;
}
.pace-slow { background: #22c55e22; color: #22c55e; }
.pace-normal { background: #3b82f622; color: #3b82f6; }
.pace-fast { background: #ef444422; color: #ef4444; }

/* Section headers */
.section-header {
    font-size: 1.25rem;
    font-weight: 600;
    color: #fff;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1f1f1f;
}

/* Form styling */
.stSlider > div > div { background: #3b82f6 !important; }
.stNumberInput input { 
    background: #141414 !important; 
    border: 1px solid #2a2a2a !important;
    color: #fff !important;
}

/* File uploader */
.stFileUploader > div { 
    background: #141414 !important;
    border: 2px dashed #2a2a2a !important;
    border-radius: 12px !important;
}
.stFileUploader > div:hover {
    border-color: #3b82f6 !important;
}

/* Success/Error messages */
.upload-success {
    background: #22c55e22;
    border: 1px solid #22c55e44;
    border-radius: 8px;
    padding: 1rem;
    color: #22c55e;
    margin: 1rem 0;
}
.upload-error {
    background: #ef444422;
    border: 1px solid #ef444444;
    border-radius: 8px;
    padding: 1rem;
    color: #ef4444;
    margin: 1rem 0;
}
.upload-info {
    background: #3b82f622;
    border: 1px solid #3b82f644;
    border-radius: 8px;
    padding: 1rem;
    color: #3b82f6;
    margin: 1rem 0;
}

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
    padding: 0.75rem 1.5rem;
    font-size: 0.95rem;
}
.stTabs [aria-selected="true"] {
    background: #2a2a2a;
    color: #fff;
}

/* Data table */
.stDataFrame { background: #141414; border-radius: 8px; }
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
if 'upload_status' not in st.session_state:
    st.session_state.upload_status = None


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


# =============================================================================
# PAGES
# =============================================================================

def render_welcome():
    """Welcome/onboarding page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-title">🧬 aevum</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Your longevity analytics companion</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0;">
            <p style="color: #9ca3af; font-size: 1.1rem; max-width: 500px; margin: 0 auto 3rem auto; line-height: 1.6;">
                Upload your blood work and get personalized insights into your biological age, 
                health systems, and pace of aging.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards in a row
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">📊</div>
                <div style="font-size: 1rem; font-weight: 600; color: #fff;">8 Health Systems</div>
                <div style="font-size: 0.85rem; color: #6b7280; margin-top: 0.5rem;">Heart, Brain, Liver, Kidney & more</div>
            </div>
            """, unsafe_allow_html=True)
        with fcol2:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🎯</div>
                <div style="font-size: 1rem; font-weight: 600; color: #fff;">Biological Age</div>
                <div style="font-size: 0.85rem; color: #6b7280; margin-top: 0.5rem;">PhenoAge-style calculation</div>
            </div>
            """, unsafe_allow_html=True)
        with fcol3:
            st.markdown("""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">⚡</div>
                <div style="font-size: 1rem; font-weight: 600; color: #fff;">Pace of Aging</div>
                <div style="font-size: 0.85rem; color: #6b7280; margin-top: 0.5rem;">Are you aging fast or slow?</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("Get Started →", use_container_width=True):
                st.session_state.page = 'upload'
                st.rerun()


def render_upload():
    """Data upload page."""
    st.markdown('<div class="main-title">🧬 aevum</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Upload your blood test data</div>', unsafe_allow_html=True)
    
    # Two column layout for desktop
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="section-header">📋 Your Information</div>', unsafe_allow_html=True)
        
        # Simple age slider
        st.markdown("**Age**")
        st.session_state.age = st.slider(
            "Your age",
            min_value=18,
            max_value=100,
            value=st.session_state.age,
            label_visibility="collapsed"
        )
        st.markdown(f"<p style='color: #6b7280; font-size: 0.9rem;'>Selected: {st.session_state.age} years old</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # File upload
        st.markdown('<div class="section-header">📄 Blood Test Results</div>', unsafe_allow_html=True)
        st.markdown("<p style='color: #6b7280; font-size: 0.9rem;'>Upload a PDF or CSV file with your blood work results</p>", unsafe_allow_html=True)
        
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
                    # Convert to labs dict
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
                            ⚠️ File uploaded but no biomarkers found. Try manual entry or a different file.
                        </div>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.markdown(f"""
                <div class="upload-error">
                    ⚠️ Error parsing file: {str(e)}<br>
                    <small>Try using CSV format or manual entry below.</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Use sample data button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧪 Use Sample Data (Demo)"):
            sample_df = create_sample_blood_data()
            labs_row = sample_df.iloc[-1].drop('date').to_dict()
            st.session_state.labs = {k: v for k, v in labs_row.items() if v is not None}
            st.rerun()
    
    with col2:
        st.markdown('<div class="section-header">✏️ Manual Entry (Optional)</div>', unsafe_allow_html=True)
        st.markdown("<p style='color: #6b7280; font-size: 0.9rem;'>Enter values directly if you don't have a file</p>", unsafe_allow_html=True)
        
        with st.expander("Enter biomarkers manually", expanded=not bool(st.session_state.labs)):
            mcol1, mcol2 = st.columns(2)
            
            with mcol1:
                st.markdown("**Metabolic**")
                glucose = st.number_input("Glucose (mg/dL)", 0.0, 500.0, 0.0, key="m_glucose")
                if glucose > 0: st.session_state.labs['Glucose'] = glucose
                
                hba1c = st.number_input("HbA1c (%)", 0.0, 15.0, 0.0, key="m_hba1c")
                if hba1c > 0: st.session_state.labs['HbA1c'] = hba1c
                
                insulin = st.number_input("Fasting Insulin (uIU/mL)", 0.0, 100.0, 0.0, key="m_insulin")
                if insulin > 0: st.session_state.labs['Fasting_Insulin'] = insulin
                
                st.markdown("**Lipids**")
                ldl = st.number_input("LDL (mg/dL)", 0.0, 300.0, 0.0, key="m_ldl")
                if ldl > 0: st.session_state.labs['LDL'] = ldl
                
                hdl = st.number_input("HDL (mg/dL)", 0.0, 150.0, 0.0, key="m_hdl")
                if hdl > 0: st.session_state.labs['HDL'] = hdl
                
                trig = st.number_input("Triglycerides (mg/dL)", 0.0, 500.0, 0.0, key="m_trig")
                if trig > 0: st.session_state.labs['Triglycerides'] = trig
            
            with mcol2:
                st.markdown("**Inflammation**")
                crp = st.number_input("hs-CRP (mg/L)", 0.0, 50.0, 0.0, key="m_crp")
                if crp > 0: st.session_state.labs['hs_CRP'] = crp
                
                st.markdown("**Liver**")
                alt = st.number_input("ALT (U/L)", 0.0, 200.0, 0.0, key="m_alt")
                if alt > 0: st.session_state.labs['ALT'] = alt
                
                ast = st.number_input("AST (U/L)", 0.0, 200.0, 0.0, key="m_ast")
                if ast > 0: st.session_state.labs['AST'] = ast
                
                st.markdown("**Kidney**")
                creat = st.number_input("Creatinine (mg/dL)", 0.0, 10.0, 0.0, key="m_creat")
                if creat > 0: st.session_state.labs['Creatinine'] = creat
                
                st.markdown("**Other**")
                albumin = st.number_input("Albumin (g/dL)", 0.0, 6.0, 0.0, key="m_albumin")
                if albumin > 0: st.session_state.labs['Albumin'] = albumin
        
        # Show current biomarkers
        if st.session_state.labs:
            st.markdown('<div class="section-header">📊 Loaded Biomarkers</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="upload-info">
                <strong>{len(st.session_state.labs)}</strong> biomarkers ready for analysis
            </div>
            """, unsafe_allow_html=True)
            
            # Show in a nice table
            labs_df = pd.DataFrame([
                {"Biomarker": k, "Value": v} 
                for k, v in st.session_state.labs.items()
            ])
            st.dataframe(labs_df, use_container_width=True, hide_index=True, height=200)
    
    # Action buttons at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    bcol1, bcol2, bcol3 = st.columns([1, 1, 1])
    
    with bcol1:
        if st.button("← Back to Home"):
            st.session_state.page = 'welcome'
            st.rerun()
    
    with bcol3:
        can_analyze = len(st.session_state.labs) > 0
        if st.button("Analyze Results →", disabled=not can_analyze, use_container_width=True):
            # Run Titan Engine
            st.session_state.results = run_titan_engine(
                st.session_state.labs,
                st.session_state.age
            )
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if not can_analyze:
            st.caption("Upload data or enter biomarkers to continue")


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
    st.markdown('<div class="main-title">🧬 aevum</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Your Health Analysis Results</div>', unsafe_allow_html=True)
    
    # Top metrics row
    mcol1, mcol2, mcol3, mcol4 = st.columns([1, 1, 1, 1])
    
    # Overall Score
    score = summary['overall_health_score']
    color = get_score_color(score)
    
    with mcol1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div class="score-circle" style="background: linear-gradient(135deg, {color}22, {color}44); border: 3px solid {color}; width: 140px; height: 140px; margin: 0 auto 1rem auto;">
                <div class="score-value" style="font-size: 2.5rem;">{score:.0f}</div>
                <div class="score-label">Health Score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Bio Age
    bio_age = summary['bio_age']
    chrono_age = summary['chrono_age']
    age_delta = bio_age - chrono_age
    delta_color = '#22c55e' if age_delta < 0 else '#ef4444' if age_delta > 2 else '#9ca3af'
    
    with mcol2:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 3rem; font-weight: 700; color: {delta_color};">{bio_age:.0f}</div>
            <div style="font-size: 0.85rem; color: #9ca3af; text-transform: uppercase; margin-bottom: 1rem;">Biological Age</div>
            <div style="font-size: 0.9rem; color: #6b7280;">
                Actual: {chrono_age} years
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Age Delta
    delta_text = f"{abs(age_delta):.1f} years younger" if age_delta < 0 else f"{age_delta:.1f} years older" if age_delta > 0 else "On track"
    delta_icon = "🎉" if age_delta < -2 else "⚠️" if age_delta > 2 else "✓"
    
    with mcol3:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{delta_icon}</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: {delta_color};">{delta_text}</div>
            <div style="font-size: 0.85rem; color: #9ca3af; text-transform: uppercase; margin-top: 0.5rem;">vs Actual Age</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Pace of Aging
    pace = summary['pace_of_aging']
    pace_color = '#22c55e' if pace < 0.95 else '#ef4444' if pace > 1.05 else '#3b82f6'
    pace_text = "Slower than average" if pace < 0.95 else "Faster than average" if pace > 1.05 else "Average pace"
    pace_icon = "🐢" if pace < 0.95 else "🐇" if pace > 1.05 else "⚖️"
    
    with mcol4:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{pace_icon}</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: {pace_color};">{pace:.2f}x</div>
            <div style="font-size: 0.85rem; color: #9ca3af; margin-top: 0.5rem;">{pace_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🫀 Body Systems", "💡 Insights", "📋 Details"])
    
    with tab1:
        st.markdown('<div class="section-header">Your Body Systems</div>', unsafe_allow_html=True)
        
        # 4-column grid for systems
        sorted_systems = sorted(systems, key=lambda x: x['score'])
        
        # Create rows of 4
        for i in range(0, len(sorted_systems), 4):
            cols = st.columns(4)
            for j, col in enumerate(cols):
                if i + j < len(sorted_systems):
                    system = sorted_systems[i + j]
                    score = system['score']
                    status = system['status']
                    color = get_score_color(score)
                    ring_class = get_ring_class(status)
                    status_class = get_status_class(status)
                    
                    # Top markers
                    top_markers = system.get('top_markers', [])[:2]
                    markers_text = ", ".join([f"{m['id']}: {m['value']:.0f}" for m in top_markers]) if top_markers else "No data"
                    
                    with col:
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
        st.markdown('<div class="section-header">Key Insights</div>', unsafe_allow_html=True)
        
        insights = results.get('insights', [])
        
        # Split into columns
        icol1, icol2 = st.columns(2)
        
        for idx, insight in enumerate(insights):
            icon = '⚠️' if 'Priority' in insight or 'Attention' in insight else '✓' if 'Excellent' in insight or 'Strong' in insight else '💡'
            
            target_col = icol1 if idx % 2 == 0 else icol2
            with target_col:
                st.markdown(f"""
                <div class="insight-item">
                    {icon} {insight}
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="section-header">Detailed Analysis</div>', unsafe_allow_html=True)
        
        dcol1, dcol2 = st.columns([1, 2])
        
        with dcol1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem; font-weight: 700; color: #3b82f6;">{results['labs_processed']}</div>
                <div style="font-size: 0.9rem; color: #9ca3af;">Biomarkers Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with dcol2:
            # All markers table
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
                st.dataframe(df, use_container_width=True, hide_index=True, height=400)
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    bcol1, bcol2, bcol3 = st.columns([1, 1, 1])
    
    with bcol1:
        if st.button("← New Analysis"):
            st.session_state.page = 'upload'
            st.session_state.labs = {}
            st.session_state.results = None
            st.rerun()
    
    with bcol3:
        if st.button("📥 Export JSON"):
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
