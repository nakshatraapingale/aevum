"""
Aevum - WHOOP-Inspired Dark Theme
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

@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes glow { 0%, 100% { box-shadow: 0 0 20px var(--accent-glow); } 50% { box-shadow: 0 0 40px var(--accent-glow); } }

h1, h2, h3, h4, h5, h6 { font-weight: 700 !important; color: var(--text-primary) !important; }
.main-title { font-size: 2rem !important; font-weight: 800 !important; color: var(--text-primary) !important; animation: fadeInUp 0.6s ease-out; }
.sub-title { font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 2rem; animation: fadeInUp 0.6s ease-out 0.1s backwards; }

.metric-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 16px; padding: 1.5rem; text-align: center; transition: all 0.3s; animation: fadeInUp 0.5s ease-out backwards; }
.metric-card:hover { transform: translateY(-4px); border-color: var(--accent); box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px var(--accent-dim); }
.metric-value { font-size: 3rem; font-weight: 800; color: var(--accent); line-height: 1; margin-bottom: 0.5rem; }
.metric-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.15em; font-weight: 600; }
.metric-delta { font-size: 0.8rem; font-weight: 700; padding: 0.3rem 0.75rem; border-radius: 20px; display: inline-block; margin-top: 0.75rem; }
.metric-delta.positive { background: rgba(0, 210, 106, 0.15); color: var(--success); }
.metric-delta.negative { background: rgba(255, 59, 92, 0.15); color: var(--danger); }

.status-optimal { background: rgba(0, 210, 106, 0.12); color: var(--success); padding: 0.4rem 0.9rem; border-radius: 6px; font-weight: 600; font-size: 0.8rem; border: 1px solid rgba(0, 210, 106, 0.2); }
.status-suboptimal { background: rgba(255, 184, 0, 0.12); color: var(--warning); padding: 0.4rem 0.9rem; border-radius: 6px; font-weight: 600; font-size: 0.8rem; border: 1px solid rgba(255, 184, 0, 0.2); }
.status-critical { background: rgba(255, 59, 92, 0.12); color: var(--danger); padding: 0.4rem 0.9rem; border-radius: 6px; font-weight: 600; font-size: 0.8rem; border: 1px solid rgba(255, 59, 92, 0.2); }

[data-testid="stSidebar"] { background: var(--bg-secondary) !important; border-right: 1px solid var(--border-color) !important; }

.stButton > button { background: var(--accent) !important; color: #000 !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 1.5rem !important; font-weight: 700 !important; text-transform: uppercase !important; transition: all 0.25s !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 10px 30px var(--accent-glow) !important; }

.stTabs [data-baseweb="tab-list"] { background: var(--bg-card) !important; border-radius: 10px !important; padding: 4px !important; border: 1px solid var(--border-color) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 8px !important; color: var(--text-muted) !important; font-weight: 600 !important; padding: 0.6rem 1.25rem !important; text-transform: uppercase !important; transition: all 0.25s !important; }
.stTabs [data-baseweb="tab"]:hover { background: var(--bg-card-hover) !important; color: var(--text-primary) !important; }
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: #000 !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }

.stTextInput > div > div > input { background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; border-radius: 8px !important; color: var(--text-primary) !important; }
.stTextInput > div > div > input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-dim) !important; }
.stTextInput > label { color: var(--text-muted) !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; font-weight: 600 !important; }

[data-testid="stFileUploader"] { background: var(--bg-card) !important; border: 2px dashed var(--border-color) !important; border-radius: 12px !important; }
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

.stProgress > div > div > div { background: linear-gradient(90deg, var(--accent), #00d4ff) !important; }
.stProgress > div > div { background: var(--bg-card) !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }

hr { border: none !important; border-top: 1px solid var(--border-color) !important; margin: 2rem 0 !important; }

@media (max-width: 768px) {
    .main .block-container { padding: 1rem !important; }
    .main-title { font-size: 1.5rem !important; }
}
</style>
"""

def apply_plotly_theme(fig):
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


def render_health_ring(overall_score, organ_scores):
    """Generate WHOOP-style health ring visualization HTML."""
    
    ring_percent = overall_score
    stroke_dasharray = f"{ring_percent * 2.51327}, 251.327"
    
    if overall_score >= 80:
        ring_color = "#00f0ff"
        status = "Excellent"
    elif overall_score >= 60:
        ring_color = "#00d26a"
        status = "Good"
    elif overall_score >= 40:
        ring_color = "#ffb800"
        status = "Fair"
    else:
        ring_color = "#ff3b5c"
        status = "Needs Attention"
    
    organ_bars = ""
    delay = 0.2
    for system, data in organ_scores.items():
        if data.get('score') is not None:
            score = data['score']
            interp = data.get('interpretation', '')
            
            if score >= 80:
                bar_color = "#00f0ff"
            elif score >= 60:
                bar_color = "#00d26a"
            elif score >= 40:
                bar_color = "#ffb800"
            else:
                bar_color = "#ff3b5c"
            
            organ_bars += f"""
            <div class="organ-row" style="animation-delay: {delay}s">
                <div class="organ-info">
                    <span class="organ-name">{system}</span>
                    <span class="organ-status">{interp}</span>
                </div>
                <div class="organ-bar-container">
                    <div class="organ-bar" style="--bar-width: {score}%; --bar-color: {bar_color}; animation-delay: {delay + 0.3}s"></div>
                </div>
                <span class="organ-score" style="color: {bar_color}">{score:.0f}</span>
            </div>
            """
            delay += 0.1
    
    html = f"""
    <style>
    .health-ring-container {{
        display: flex;
        gap: 3rem;
        padding: 2rem;
        background: #0a0a0a;
        border-radius: 20px;
        border: 1px solid #1a1a1a;
        animation: hrFadeIn 0.5s ease-out;
    }}
    @keyframes hrFadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .ring-section {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 220px;
    }}
    .ring-wrapper {{
        position: relative;
        width: 200px;
        height: 200px;
    }}
    .ring-svg {{
        transform: rotate(-90deg);
        width: 200px;
        height: 200px;
    }}
    .ring-bg {{
        fill: none;
        stroke: #1a1a1a;
        stroke-width: 12;
    }}
    .ring-progress {{
        fill: none;
        stroke: {ring_color};
        stroke-width: 12;
        stroke-linecap: round;
        stroke-dasharray: 0, 251.327;
        filter: drop-shadow(0 0 10px {ring_color}40);
        animation: ringFill 1.5s ease-out forwards;
    }}
    @keyframes ringFill {{
        to {{ stroke-dasharray: {stroke_dasharray}; }}
    }}
    .ring-center {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }}
    .ring-score {{
        font-size: 3.5rem;
        font-weight: 800;
        color: {ring_color};
        line-height: 1;
        text-shadow: 0 0 30px {ring_color}50;
    }}
    .ring-label {{
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 0.25rem;
    }}
    .ring-status {{
        font-size: 0.9rem;
        color: {ring_color};
        font-weight: 600;
        margin-top: 1rem;
        padding: 0.4rem 1rem;
        background: {ring_color}15;
        border-radius: 20px;
        border: 1px solid {ring_color}30;
    }}
    .organs-section {{
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }}
    .organs-title {{
        font-size: 0.7rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }}
    .organ-row {{
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid #1a1a1a;
        opacity: 0;
        animation: slideIn 0.4s ease-out forwards;
    }}
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-10px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    .organ-row:last-child {{ border-bottom: none; }}
    .organ-info {{
        width: 120px;
        display: flex;
        flex-direction: column;
    }}
    .organ-name {{
        font-size: 0.9rem;
        color: #ffffff;
        font-weight: 600;
    }}
    .organ-status {{
        font-size: 0.7rem;
        color: #6b7280;
    }}
    .organ-bar-container {{
        flex: 1;
        height: 8px;
        background: #1a1a1a;
        border-radius: 4px;
        overflow: hidden;
    }}
    .organ-bar {{
        height: 100%;
        width: 0;
        background: var(--bar-color);
        border-radius: 4px;
        animation: barFill 1s ease-out forwards;
        box-shadow: 0 0 10px var(--bar-color);
    }}
    @keyframes barFill {{
        to {{ width: var(--bar-width); }}
    }}
    .organ-score {{
        font-size: 1rem;
        font-weight: 700;
        width: 35px;
        text-align: right;
    }}
    @media (max-width: 768px) {{
        .health-ring-container {{
            flex-direction: column;
            align-items: center;
        }}
        .ring-section {{ margin-bottom: 1.5rem; }}
    }}
    </style>
    
    <div class="health-ring-container">
        <div class="ring-section">
            <div class="ring-wrapper">
                <svg class="ring-svg" viewBox="0 0 100 100">
                    <circle class="ring-bg" cx="50" cy="50" r="40"/>
                    <circle class="ring-progress" cx="50" cy="50" r="40"/>
                </svg>
                <div class="ring-center">
                    <div class="ring-score">{overall_score:.0f}</div>
                    <div class="ring-label">Health Score</div>
                </div>
            </div>
            <div class="ring-status">{status}</div>
        </div>
        
        <div class="organs-section">
            <div class="organs-title">System Breakdown</div>
            {organ_bars}
        </div>
    </div>
    """
    
    return html

