"""
Aevum - Longevity Medicine Platform
Integrates blood biomarkers with WHOOP biometrics for comprehensive health analysis.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.optimal_ranges import normalize_biomarker_name
from modules.longevity_engine import (calculate_phenoage, calculate_organ_system_scores,
                                       estimate_dunedin_pace)
from modules.data_extraction import pdf_to_dataframe, parse_whoop_csv
from modules.auth import (render_auth_page, is_authenticated, get_current_user, logout_user)
from styles import AEVUM_CSS, apply_plotly_theme, render_health_ring

# Page config
st.set_page_config(
    page_title="Aevum - Longevity Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply modern dark theme
st.markdown(AEVUM_CSS, unsafe_allow_html=True)


def create_age_gauge(chronological_age, biological_age):
    """Create biological age gauge visualization."""
    diff = biological_age - chronological_age
    color = "green" if diff < -2 else "orange" if diff < 2 else "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=biological_age,
        delta={'reference': chronological_age, 'relative': False, 'position': "bottom"},
        title={'text': "Biological Age", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [chronological_age - 15, chronological_age + 15], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'steps': [
                {'range': [chronological_age - 15, chronological_age - 5], 'color': 'lightgreen'},
                {'range': [chronological_age - 5, chronological_age + 5], 'color': 'lightyellow'},
                {'range': [chronological_age + 5, chronological_age + 15], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': chronological_age
            }
        }
    ))
    fig.update_layout(
        height=300, 
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b0', family='Inter')
    )
    return fig


def create_pace_speedometer(pace):
    """Create pace of aging speedometer."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pace,
        title={'text': "Pace of Aging<br><span style='font-size:0.8em'>years aged per year</span>"},
        gauge={
            'axis': {'range': [0.7, 1.3], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0.7, 0.9], 'color': 'lightgreen'},
                {'range': [0.9, 1.1], 'color': 'lightyellow'},
                {'range': [1.1, 1.3], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1.0
            }
        }
    ))
    fig.update_layout(
        height=250, 
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b0', family='Inter')
    )
    return fig


# Initialize session state with empty data
if 'blood_data' not in st.session_state:
    st.session_state.blood_data = pd.DataFrame()
if 'whoop_data' not in st.session_state:
    st.session_state.whoop_data = pd.DataFrame()
if 'chronological_age' not in st.session_state:
    st.session_state.chronological_age = 35
if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = False


def render_upload_screen():
    """Render the data upload screen."""
    st.markdown('<div class="main-title">aevum</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Upload your health data to get started</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;">
            <h3 style="color: #fff; margin-bottom: 1rem; font-size: 1.1rem;">Blood Test Results</h3>
            <p style="color: #6b7280; font-size: 0.85rem; margin-bottom: 1rem;">Upload your blood work PDF or CSV file</p>
        </div>
        """, unsafe_allow_html=True)
        
        blood_file = st.file_uploader("Blood Results", type=['pdf', 'csv'], label_visibility="collapsed")
        
        st.markdown("""
        <div style="background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 16px; padding: 2rem; margin: 1.5rem 0;">
            <h3 style="color: #fff; margin-bottom: 1rem; font-size: 1.1rem;">WHOOP Data (Optional)</h3>
            <p style="color: #6b7280; font-size: 0.85rem; margin-bottom: 1rem;">Export from WHOOP app for correlations</p>
        </div>
        """, unsafe_allow_html=True)
        
        whoop_file = st.file_uploader("WHOOP Export", type=['csv'], label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.session_state.chronological_age = st.number_input("Your Age", 18, 100, st.session_state.chronological_age)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Process uploaded files immediately when they're uploaded
        if blood_file is not None:
            try:
                if blood_file.name.lower().endswith('.pdf'):
                    df = pdf_to_dataframe(blood_file)
                else:
                    # CSV upload
                    df = pd.read_csv(blood_file)
                    # Ensure date column exists
                    if 'date' not in df.columns:
                        df['date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
                
                if len(df) > 0:
                    st.session_state.blood_data = df
                    st.success(f"Loaded {len(df.columns)-1} biomarkers!")
                else:
                    st.warning("No data found in file")
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("**CSV Format:** Create a CSV with columns: date, Glucose, HbA1c, Cholesterol, etc. Example:")
                st.code("date,Glucose,HbA1c,Cholesterol\n2024-01-15,95,5.2,180", language="csv")
        
        if whoop_file is not None:
            try:
                st.session_state.whoop_data = parse_whoop_csv(whoop_file)
                st.success("WHOOP data loaded!")
            except Exception as e:
                st.error(f"Error: {e}")
        
        analyze_disabled = len(st.session_state.blood_data) == 0
        if st.button("View Dashboard", use_container_width=True, type="primary", disabled=analyze_disabled):
            st.session_state.data_uploaded = True
            st.rerun()
        
        if analyze_disabled:
            st.caption("Upload a blood test file to enable analysis")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()


def render_dashboard():
    """Render the main dashboard with analysis."""
    user = get_current_user()
    
    st.markdown('<div class="main-title">aevum</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Longevity Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"**{user['email']}**")
        
        st.divider()
        
        st.session_state.chronological_age = st.number_input("Age", 18, 100, st.session_state.chronological_age)
        
        st.divider()
        
        if st.button("Upload New Data", use_container_width=True):
            st.session_state.data_uploaded = False
            st.session_state.blood_data = pd.DataFrame()
            st.session_state.whoop_data = pd.DataFrame()
            st.rerun()
        
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Get blood data
    blood_df = st.session_state.blood_data
    latest_blood = blood_df.iloc[-1].to_dict() if len(blood_df) > 0 else {}
    
    # Render the main content (no tabs)
    render_health_dashboard(latest_blood)


def main():
    # Check authentication first
    if not is_authenticated():
        render_auth_page()
        return
    
    # Check if data is uploaded
    if not st.session_state.get('data_uploaded', False) or len(st.session_state.blood_data) == 0:
        render_upload_screen()
    else:
        render_dashboard()


def render_health_dashboard(latest_blood):
    """Render the simplified health dashboard with health score, bio age, and pace."""
    
    # Calculate organ scores for health ring
    organ_scores = calculate_organ_system_scores(latest_blood)
    valid_scores = [data['score'] for data in organ_scores.values() if data.get('score') is not None]
    overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    # Health Ring at the top
    health_ring_html = render_health_ring(overall_score, organ_scores)
    st.markdown(health_ring_html, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Biological Age and Pace of Aging side by side
    col1, col2 = st.columns(2)
    
    # Check if we have required PhenoAge markers
    required = ['Albumin', 'Creatinine', 'Glucose', 'hs-CRP', 'Lymphocyte_pct', 'MCV', 'RDW', 'ALP', 'WBC']
    has_phenoage = all(k in latest_blood or normalize_biomarker_name(k) in latest_blood for k in required[:5])
    
    with col1:
        st.markdown("### Biological Age")
        if has_phenoage:
            try:
                phenoage_result = calculate_phenoage(
                    chronological_age=st.session_state.chronological_age,
                    albumin=latest_blood.get('Albumin', 4.4),
                    creatinine=latest_blood.get('Creatinine', 0.9),
                    glucose=latest_blood.get('Glucose', 90),
                    crp=latest_blood.get('hs-CRP', 0.5),
                    lymphocyte_pct=latest_blood.get('Lymphocyte_pct', 33),
                    mcv=latest_blood.get('MCV', 87),
                    rdw=latest_blood.get('RDW', 12.8),
                    alp=latest_blood.get('ALP', 50),
                    wbc=latest_blood.get('WBC', 5.5)
                )
                
                st.plotly_chart(create_age_gauge(st.session_state.chronological_age, phenoage_result['phenoage']), use_container_width=True)
                
                delta = phenoage_result['age_acceleration']
                if delta < -2:
                    st.success(f"You're {abs(delta):.1f} years younger biologically!")
                elif delta > 2:
                    st.warning(f"You're {delta:.1f} years older biologically.")
                else:
                    st.info("Aging at a normal rate.")
                
            except Exception as e:
                st.error(f"Calculation error: {e}")
                phenoage_result = {'pace': 1.0}
        else:
            st.info("Upload more biomarkers for PhenoAge")
            st.caption("Need: Albumin, Creatinine, Glucose, CRP, Lymphocyte%")
            phenoage_result = {'pace': 1.0}
    
    with col2:
        st.markdown("### Pace of Aging")
        st.plotly_chart(create_pace_speedometer(phenoage_result.get('pace', 1.0)), use_container_width=True)
        
        # DunedinPACE estimate
        dunedin = estimate_dunedin_pace({
            'crp': latest_blood.get('hs-CRP', 0.5),
            'glucose': latest_blood.get('Glucose', 90),
            'hba1c': latest_blood.get('HbA1c', 5.2),
            'hdl': latest_blood.get('HDL Cholesterol', 60),
            'triglycerides': latest_blood.get('Triglycerides', 100),
            'albumin': latest_blood.get('Albumin', 4.4),
            'creatinine': latest_blood.get('Creatinine', 0.9)
        })
        
        if dunedin:
            st.metric("DunedinPACE", f"{dunedin['pace_estimate']:.2f}", 
                     help="<1.0 = slower aging, >1.0 = faster aging")
            st.caption(dunedin['interpretation'])


if __name__ == "__main__":
    main()
