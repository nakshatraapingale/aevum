"""
Aevum - WHOOP-Inspired Dark Theme
Clean, minimal, athletic design with Nunito font and teal accents.
"""

AEVUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary: #000000;
    --bg-secondary: #0d0d0d;
    --bg-card: #141414;
    --bg-card-hover: #1a1a1a;
    --border-color: #222222;
    --text-primary: #ffffff;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --accent: #00f0ff;
    --accent-dim: rgba(0, 240, 255, 0.15);
    --accent-glow: rgba(0, 240, 255, 0.4);
    --success: #00d26a;
    --warning: #ffb800;
    --danger: #ff3b5c;
}

* { font-family: 'Nunito', sans-serif !important; }

.stApp { background: var(--bg-primary) !important; }

#MainMenu, footer, header {visibility: hidden;}

.main .block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

/* ANIMATIONS */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px var(--accent-glow); }
    50% { box-shadow: 0 0 40px var(--accent-glow), 0 0 60px rgba(0, 240, 255, 0.2); }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

.animate-glow { animation: glow 3s ease-in-out infinite; }
.animate-float { animation: float 3s ease-in-out infinite; }

/* TYPOGRAPHY */
h1, h2, h3, h4, h5, h6 { font-weight: 700 !important; color: var(--text-primary) !important; }

.main-title {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
    animation: fadeInUp 0.6s ease-out;
}

.sub-title {
    font-size: 0.95rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin-bottom: 2rem;
    animation: fadeInUp 0.6s ease-out 0.1s backwards;
}

/* METRIC CARDS */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.5s ease-out backwards;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 30px var(--accent-dim);
}

.metric-card:hover::before { opacity: 1; }

.metric-value {
    font-size: 3rem;
    font-weight: 800;
    color: var(--accent);
    line-height: 1;
    margin-bottom: 0.5rem;
    transition: transform 0.3s ease;
}

.metric-card:hover .metric-value { transform: scale(1.05); }

.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 600;
}

.metric-delta {
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.3rem 0.75rem;
    border-radius: 20px;
    display: inline-block;
    margin-top: 0.75rem;
}

.metric-delta.positive { background: rgba(0, 210, 106, 0.15); color: var(--success); }
.metric-delta.negative { background: rgba(255, 59, 92, 0.15); color: var(--danger); }

/* STATUS BADGES */
.status-optimal {
    background: rgba(0, 210, 106, 0.12);
    color: var(--success);
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.8rem;
    border: 1px solid rgba(0, 210, 106, 0.2);
}

.status-suboptimal {
    background: rgba(255, 184, 0, 0.12);
    color: var(--warning);
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.8rem;
    border: 1px solid rgba(255, 184, 0, 0.2);
}

.status-critical {
    background: rgba(255, 59, 92, 0.12);
    color: var(--danger);
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.8rem;
    border: 1px solid rgba(255, 59, 92, 0.2);
}

/* SIDEBAR */
[data-testid="stSidebar"] { background: var(--bg-secondary) !important; border-right: 1px solid var(--border-color) !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-size: 0.85rem !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; color: var(--text-muted) !important;
}

/* BUTTONS */
.stButton > button {
    background: var(--accent) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px var(--accent-glow) !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid var(--border-color) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.25rem !important;
    transition: all 0.25s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.stTabs [data-baseweb="tab"]:hover { background: var(--bg-card-hover) !important; color: var(--text-primary) !important; }
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: #000000 !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }

/* INPUTS */
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    transition: all 0.25s ease !important;
}

.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
}

.stTextInput > label, .stNumberInput > label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 600 !important;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border-color) !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
    background: rgba(0, 240, 255, 0.03) !important;
}

/* PROGRESS */
.stProgress > div > div > div { background: linear-gradient(90deg, var(--accent), #00d4ff) !important; }
.stProgress > div > div { background: var(--bg-card) !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }

/* DIVIDER */
hr { border: none !important; border-top: 1px solid var(--border-color) !important; margin: 2rem 0 !important; }

/* RESPONSIVE */
@media (max-width: 768px) {
    .main .block-container { padding: 1rem !important; }
    .main-title { font-size: 1.5rem !important; }
    .metric-value { font-size: 2rem; }
}
</style>
"""

def apply_plotly_theme(fig):
    """Apply WHOOP-inspired dark theme to Plotly figure."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9ca3af', family='Nunito'),
        title_font=dict(color='#ffffff', size=14),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', linecolor='#222222', tickfont=dict(color='#6b7280')),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', linecolor='#222222', tickfont=dict(color='#6b7280')),
        legend=dict(font=dict(color='#9ca3af')),
        colorway=['#00f0ff', '#00d26a', '#ffb800', '#ff3b5c', '#a855f7', '#3b82f6']
    )
    return fig
