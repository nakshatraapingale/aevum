"""
Aevum - Longevity Medicine Platform
Integrates blood biomarkers with WHOOP biometrics for comprehensive health analysis.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.optimal_ranges import (LONGEVITY_OPTIMAL_RANGES, classify_value, 
                                     get_optimal_range, normalize_biomarker_name)
from modules.longevity_engine import (calculate_phenoage, calculate_organ_system_scores,
                                       estimate_dunedin_pace, get_phenoage_requirements)
from modules.data_extraction import (create_sample_blood_data, create_sample_whoop_data, pdf_to_dataframe,
                                      merge_blood_whoop_data, parse_whoop_csv)
from modules.correlation_analysis import (calculate_correlation_matrix, lagging_indicator_analysis,
                                           performance_ceiling_analysis, cross_correlation_heatmap_data)
from modules.insights_engine import generate_protocol, summarize_health_status
from modules.auth import (render_auth_page, is_authenticated, get_current_user,
                          logout_user, save_user_data, load_user_data)
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


def create_traffic_light_chart(biomarkers_df):
    """Create traffic light visualization for biomarker status."""
    colors = {'optimal': '#00d26a', 'suboptimal': '#ffb800', 'low': '#ff3b5c', 
              'high': '#ff3b5c', 'unknown': '#6b7280'}
    
    fig = go.Figure()
    
    for idx, row in biomarkers_df.iterrows():
        fig.add_trace(go.Bar(
            y=[row['biomarker']],
            x=[1],
            orientation='h',
            marker_color=colors.get(row['status'], '#6c757d'),
            text=f"{row['value']:.1f} ({row['status']})",
            textposition='inside',
            hovertemplate=f"<b>{row['biomarker']}</b><br>Value: {row['value']:.1f}<br>Optimal: {row['optimal_range']}<br>Status: {row['status']}<extra></extra>"
        ))
    
    fig.update_layout(
        showlegend=False,
        height=max(400, len(biomarkers_df) * 25),
        margin=dict(l=150, r=50, t=30, b=30),
        xaxis={'visible': False},
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b0', family='Inter')
    )
    return fig


def create_organ_system_radar(organ_scores):
    """Create radar chart for organ system scores."""
    systems = []
    scores = []
    for system, data in organ_scores.items():
        if data.get('score') is not None:
            systems.append(system)
            scores.append(data['score'])
    
    if not systems:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=systems + [systems[0]],
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.3)',
        line=dict(color='#00f0ff', width=2),
        name='Your Score'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[80] * (len(systems) + 1),
        theta=systems + [systems[0]],
        line=dict(color='#00d26a', dash='dash', width=1),
        name='Optimal Threshold'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color='#a0a0b0')),
            bgcolor='rgba(0,0,0,0)',
            angularaxis=dict(tickfont=dict(color='#a0a0b0'))
        ),
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b0', family='Inter'),
        legend=dict(font=dict(color='#a0a0b0'))
    )
    return fig


def create_correlation_heatmap(corr_data):
    """Create heatmap for blood-WHOOP correlations."""
    if 'error' in corr_data:
        return None
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_data['correlations'],
        x=corr_data['whoop_metrics'],
        y=corr_data['blood_markers'],
        colorscale='RdBu_r',
        zmid=0,
        text=np.round(corr_data['correlations'], 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title='Blood Marker ↔ WHOOP Metric Correlations',
        height=max(400, len(corr_data['blood_markers']) * 30),
        margin=dict(l=150, r=50, t=50, b=100),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b0', family='Inter'),
        title_font=dict(color='#ffffff')
    )
    return fig


def create_lag_analysis_chart(lag_results):
    """Create visualization for lag analysis results."""
    if not lag_results or 'error' in lag_results:
        return None
    
    df = pd.DataFrame(lag_results['analysis'])
    if df.empty:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['lag_days'],
        y=df['correlation'],
        mode='lines+markers',
        line=dict(color='#00f0ff', width=2),
        marker=dict(size=8)
    ))
    
    optimal = lag_results.get('optimal_lag')
    if optimal:
        fig.add_vline(x=optimal['lag_days'], line_dash="dash", line_color="#00d4ff",
                      annotation_text=f"Optimal lag: {optimal['lag_days']} days",
                      annotation_font_color="#a0a0b0")
    
    fig.add_hline(y=0, line_dash="dot", line_color="#4b5563")
    fig.update_layout(
        title='Time-Lagged Correlation Analysis',
        xaxis_title='Lag (days) - Positive = Blood marker leads',
        yaxis_title='Correlation coefficient',
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b0', family='Inter'),
        title_font=dict(color='#ffffff'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
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
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Bio-Age", "Optimal Zone", "Correlations", "Protocol"])
    
    blood_df = st.session_state.blood_data
    latest_blood = blood_df.iloc[-1].to_dict() if len(blood_df) > 0 else {}
    
    with tab1:
        render_bioage_tab(latest_blood)
    
    with tab2:
        render_optimal_zone_tab(latest_blood)
    
    with tab3:
        render_correlation_tab()
    
    with tab4:
        render_protocol_tab(latest_blood)


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


def render_bioage_tab(latest_blood):
    """Render Bio-Age Summary tab."""
    st.header("Biological Age Assessment")
    
    col1, col2 = st.columns(2)
    
    # Check if we have required PhenoAge markers
    required = ['Albumin', 'Creatinine', 'Glucose', 'hs-CRP', 'Lymphocyte_pct', 'MCV', 'RDW', 'ALP', 'WBC']
    has_phenoage = all(k in latest_blood or normalize_biomarker_name(k) in latest_blood for k in required[:5])
    
    with col1:
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
                    st.success(f"🎉 Your biological age is {abs(delta):.1f} years YOUNGER than your chronological age!")
                elif delta > 2:
                    st.warning(f"Your biological age is {delta:.1f} years OLDER than your chronological age.")
                else:
                    st.info("You're aging at a normal rate.")
                
            except Exception as e:
                st.error(f"PhenoAge calculation error: {e}")
                phenoage_result = {'pace': 1.0}
        else:
            st.warning("Insufficient biomarkers for PhenoAge calculation")
            st.info("Required: Albumin, Creatinine, Glucose, CRP, Lymphocyte%, MCV, RDW, ALP, WBC")
            phenoage_result = {'pace': 1.0}
    
    with col2:
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
            st.metric("DunedinPACE Estimate", f"{dunedin['pace_estimate']:.2f}", 
                     help="Estimated pace of aging. <1.0 = slower aging, >1.0 = faster aging")
            st.caption(dunedin['interpretation'])
    
    # Organ System Scores - WHOOP-style visualization
    organ_scores = calculate_organ_system_scores(latest_blood)
    
    # Calculate overall health score (average of all organ scores)
    valid_scores = [data['score'] for data in organ_scores.values() if data.get('score') is not None]
    overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    # Render the WHOOP-style health ring
    health_ring_html = render_health_ring(overall_score, organ_scores)
    st.markdown(health_ring_html, unsafe_allow_html=True)


def render_optimal_zone_tab(latest_blood):
    """Render Optimal Zone tab with traffic light system."""
    st.header("Longevity Optimal Zone Analysis")
    st.caption("Green = Optimal | Yellow = Lab Normal but Longevity Sub-Optimal | Red = Outside Range")
    
    # Build biomarker status dataframe
    biomarker_status = []
    for marker, value in latest_blood.items():
        if marker == 'date' or value is None or pd.isna(value):
            continue
        try:
            value = float(value)
        except:
            continue
        
        optimal = get_optimal_range(marker)
        if optimal:
            classification = classify_value(marker, value)
            biomarker_status.append({
                'biomarker': marker,
                'value': value,
                'optimal_low': optimal['optimal_low'],
                'optimal_high': optimal['optimal_high'],
                'optimal_range': f"{optimal['optimal_low']}-{optimal['optimal_high']}",
                'unit': optimal['unit'],
                'category': optimal['category'],
                'status': classification['status'],
                'message': classification['message']
            })
    
    if biomarker_status:
        status_df = pd.DataFrame(biomarker_status)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        optimal_count = len(status_df[status_df['status'] == 'optimal'])
        suboptimal_count = len(status_df[status_df['status'] == 'suboptimal'])
        critical_count = len(status_df[status_df['status'].isin(['low', 'high'])])
        
        with col1:
            st.metric("Optimal", optimal_count, f"{optimal_count/len(status_df)*100:.0f}%")
        with col2:
            st.metric("Sub-Optimal", suboptimal_count)
        with col3:
            st.metric("Critical", critical_count)
        with col4:
            st.metric("Total Markers", len(status_df))
        
        # Filter by category
        categories = ['All'] + list(status_df['category'].unique())
        selected_cat = st.selectbox("Filter by System", categories)
        
        if selected_cat != 'All':
            status_df = status_df[status_df['category'] == selected_cat]
        
        # Traffic light visualization
        st.plotly_chart(create_traffic_light_chart(status_df), use_container_width=True)
        
        # Detailed table
        with st.expander("📋 Detailed Biomarker Table"):
            st.dataframe(status_df[['biomarker', 'value', 'optimal_range', 'unit', 'status', 'message']], 
                        use_container_width=True, hide_index=True)
    else:
        st.warning("No biomarker data available for analysis.")


def render_correlation_tab():
    """Render Correlation Matrix tab."""
    st.header("Cross-Dataset Correlation Analysis")
    
    blood_df = st.session_state.blood_data
    whoop_df = st.session_state.whoop_data
    
    # Merge data
    try:
        merged_df = merge_blood_whoop_data(blood_df.copy(), whoop_df.copy())
    except Exception as e:
        st.error(f"Error merging data: {e}")
        return
    
    # Define columns for analysis
    blood_cols = [c for c in merged_df.columns if c in LONGEVITY_OPTIMAL_RANGES or normalize_biomarker_name(c) in LONGEVITY_OPTIMAL_RANGES]
    whoop_cols = [c for c in merged_df.columns if any(x in c.lower() for x in ['hrv', 'rhr', 'recovery', 'strain', 'sleep'])]
    
    if not blood_cols or not whoop_cols:
        st.warning("Insufficient data for correlation analysis. Need both blood markers and WHOOP metrics.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Correlation Heatmap")
        corr_data = cross_correlation_heatmap_data(merged_df, blood_cols[:10], whoop_cols[:6])
        heatmap = create_correlation_heatmap(corr_data)
        if heatmap:
            st.plotly_chart(heatmap, use_container_width=True)
    
    with col2:
        st.subheader("⏱️ Lagging Indicator Analysis")
        st.caption("Does a blood marker change predict WHOOP metric changes days later?")
        
        blood_marker = st.selectbox("Blood Marker", blood_cols[:10])
        whoop_metric = st.selectbox("WHOOP Metric", whoop_cols[:6])
        
        if blood_marker and whoop_metric:
            lag_results = lagging_indicator_analysis(merged_df, blood_marker, whoop_metric)
            
            if 'error' not in lag_results:
                lag_chart = create_lag_analysis_chart(lag_results)
                if lag_chart:
                    st.plotly_chart(lag_chart, use_container_width=True)
                
                if lag_results.get('optimal_lag'):
                    st.info(lag_results['interpretation'])
    
    # Performance Ceiling Analysis
    st.subheader("🚀 Performance Ceiling Analysis")
    st.caption("Do nutrient deficiencies limit your peak performance?")
    
    nutrient_markers = [c for c in blood_cols if any(x in c for x in ['Vitamin', 'Ferritin', 'Iron', 'B12', 'Folate', 'Magnesium'])]
    perf_metrics = [c for c in whoop_cols if any(x in c.lower() for x in ['strain', 'recovery', 'hrv'])]
    
    if nutrient_markers and perf_metrics:
        ceiling_results = performance_ceiling_analysis(merged_df, nutrient_markers[:5], perf_metrics[:3])
        
        if ceiling_results.get('significant_ceilings'):
            st.warning(ceiling_results['summary'])
            with st.expander("View Details"):
                for effect in ceiling_results['significant_ceilings']:
                    st.write(f"**{effect['nutrient']}** → {effect['performance_metric']}")
                    st.write(f"  Deficient group mean: {effect['deficient_mean']:.1f}")
                    st.write(f"  Adequate group mean: {effect['adequate_mean']:.1f}")
                    st.write(f"  Effect size (Cohen's d): {effect['cohens_d']:.2f}")
        else:
            st.success("No significant performance ceiling effects detected from current nutrient status.")


def render_protocol_tab(latest_blood):
    """Render Actionable Protocol tab."""
    st.header("Actionable Intervention Protocol")
    
    # Get organ scores for summary
    organ_scores = calculate_organ_system_scores(latest_blood)
    health_summary = summarize_health_status(latest_blood, organ_scores)
    
    # Overall grade card
    grade_colors = {'A': '#28a745', 'B': '#20c997', 'C': '#ffc107', 'D': '#fd7e14', 'F': '#dc3545'}
    grade = health_summary['overall_grade']
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {grade_colors[grade]}aa, {grade_colors[grade]}); border-radius: 15px; margin-bottom: 2rem;">
            <h1 style="color: white; font-size: 4rem; margin: 0;">{grade}</h1>
            <p style="color: white; font-size: 1.2rem;">{health_summary['overall_message']}</p>
            <p style="color: rgba(255,255,255,0.8);">{health_summary['optimal_percentage']:.0f}% of markers in optimal range</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate protocols
    protocols = generate_protocol(latest_blood, top_n=5)
    
    if protocols:
        st.subheader("🎯 Top Priority Interventions")
        
        for i, protocol in enumerate(protocols, 1):
            severity_color = {'high': '🔴', 'moderate': '🟡', 'mild': '🟢'}.get(protocol.get('deviation_severity', 'moderate'), '🟡')
            
            with st.expander(f"{severity_color} Priority {i}: {protocol['target_marker']} ({protocol['category']})", expanded=(i <= 2)):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.metric("Current Value", f"{protocol['current_value']:.1f}")
                    st.caption(f"Optimal Range: {protocol['optimal_range']}")
                    st.caption(f"Severity: {protocol.get('deviation_severity', 'unknown').title()}")
                
                with col2:
                    st.markdown("**Recommended Interventions:**")
                    for intervention in protocol.get('interventions', []):
                        st.markdown(f"• {intervention}")
                    
                    st.caption(f"*Mechanism: {protocol.get('mechanism', 'N/A')}*")
    else:
        st.success("🎉 All biomarkers are within optimal ranges! Continue current lifestyle practices.")
    
    # Weakest systems
    if health_summary.get('weakest_systems'):
        st.subheader("Systems Needing Most Attention")
        for system in health_summary['weakest_systems']:
            st.warning(f"**{system['system']}**: Score {system['score']:.0f}/100 - {system['interpretation']}")
    
    # Download report
    st.subheader("Export Report")
    if st.button("Generate PDF Report"):
        st.info("PDF export feature coming soon! For now, use browser print function.")


if __name__ == "__main__":
    main()
