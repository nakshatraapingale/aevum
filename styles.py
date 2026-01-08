"""
Aevum - Modern Dark Theme Styles
Beautiful glassmorphism design with smooth animations.
"""

AEVUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: rgba(255, 255, 255, 0.03);
    --bg-card-hover: rgba(255, 255, 255, 0.06);
    --border-color: rgba(255, 255, 255, 0.08);
    --text-primary: #ffffff;
    --text-secondary: #a0a0b0;
    --text-muted: #606070;
    --accent-primary: #6366f1;
    --accent-secondary: #8b5cf6;
    --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

#MainMenu, footer, header {visibility: hidden;}

.main .block-container {
    padding: 2rem 3rem !important;
    max-width: 1400px !important;
}

/* Typography */
.main-title {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem !important;
}

.sub-title {
    font-size: 1rem;
    color: #a0a0b0;
    margin-bottom: 2rem;
}

/* Metric Cards */
.metric-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 1.75rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
    border-color: rgba(99, 102, 241, 0.4);
}

.metric-value {
    font-size: 2.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}

.metric-label {
    font-size: 0.8rem;
    color: #a0a0b0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.5rem;
}

.metric-delta {
    font-size: 0.875rem;
    font-weight: 600;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    display: inline-block;
    margin-top: 0.75rem;
}

.metric-delta.positive {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
}

.metric-delta.negative {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
}

/* Status Badges */
.status-optimal {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    padding: 0.4rem 0.9rem;
    border-radius: 20px;
    font-weight: 500;
    font-size: 0.85rem;
}

.status-suboptimal {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    padding: 0.4rem 0.9rem;
    border-radius: 20px;
    font-weight: 500;
    font-size: 0.85rem;
}

.status-critical {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    padding: 0.4rem 0.9rem;
    border-radius: 20px;
    font-weight: 500;
    font-size: 0.85rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12121a 0%, #0a0a0f 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}

[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.5rem !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.5) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border-radius: 16px !important;
    padding: 0.5rem !important;
    gap: 0.25rem !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 12px !important;
    color: #a0a0b0 !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.75rem 1.25rem !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    color: white !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 2px dashed rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #6366f1 !important;
    background: rgba(99, 102, 241, 0.05) !important;
}

/* Plotly Charts */
.js-plotly-plot {
    border-radius: 16px !important;
}

/* Progress Bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6366f1, #a855f7) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.03) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* Grade Badges */
.grade-a { background: linear-gradient(135deg, #10b981, #059669); }
.grade-b { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.grade-c { background: linear-gradient(135deg, #f59e0b, #d97706); }
.grade-d { background: linear-gradient(135deg, #f97316, #ea580c); }
.grade-f { background: linear-gradient(135deg, #ef4444, #dc2626); }

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }
    50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.5); }
}

.animate-glow {
    animation: glow 3s ease-in-out infinite;
}

/* DataFrames */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}

/* Responsive */
@media (max-width: 768px) {
    .main .block-container { padding: 1rem !important; }
    .main-title { font-size: 1.75rem !important; }
    .metric-value { font-size: 2rem; }
}
</style>
"""

def apply_plotly_theme(fig):
    """Apply dark theme to Plotly figure."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0b0', family='Inter, sans-serif'),
        title_font=dict(color='#ffffff'),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#a0a0b0')
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#a0a0b0')
        ),
        legend=dict(font=dict(color='#a0a0b0'))
    )
    return fig
