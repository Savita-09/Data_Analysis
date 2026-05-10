import streamlit as st


def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #141d2e;
        --bg-card-hover: #192035;
        --accent-primary: #00d4ff;
        --accent-secondary: #7c3aed;
        --accent-green: #10b981;
        --accent-amber: #f59e0b;
        --accent-rose: #f43f5e;
        --text-primary: #f0f4ff;
        --text-secondary: #8b9cc8;
        --text-muted: #4a5568;
        --border: #1e2d45;
        --border-bright: #2a3f60;
        --glow: 0 0 20px rgba(0, 212, 255, 0.15);
        --font-sans: 'DM Sans', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
        --font-display: 'Space Mono', monospace;
    }

    /* ── Global Reset ── */
    .stApp {
        background: var(--bg-primary) !important;
        background-image:
            radial-gradient(ellipse at 20% 0%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 0%, rgba(0, 212, 255, 0.06) 0%, transparent 50%);
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
    }

    .main .block-container {
        padding-top: 2rem !important;
        max-width: 1400px !important;
    }

    /* ── Header ── */
    .app-header {
        text-align: center;
    }

    .header-icon {
        font-size: 4rem;
        margin-bottom: 0.4rem;
        filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5));
    }

    .app-title {
        font-family: var(--font-display) !important;
        font-size: 2.9rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -1px;
        margin: 0 0 0.5rem !important;
        text-shadow: 0 0 40px rgba(0, 212, 255, 0.3);
    }

    .app-title .accent {
        color: var(--accent-primary);
    }

    .app-subtitle {
        color: var(--text-secondary) !important;
        font-size: 1rem !important;
        letter-spacing: 0.08em;
        font-weight: 300;
    }

    /* ── Upload Hero ── */
    .upload-hero {
        text-align: center;
        padding: 3rem 2rem 2rem;
        max-width: 600px;
        margin: 0 auto;
    }

    .hero-glyph {
        font-size: 4rem;
        color: var(--accent-primary);
        opacity: 0.6;
        margin-bottom: 1rem;
        animation: pulse 3s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.4; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.05); }
    }

    .upload-hero h2 {
        font-family: var(--font-display) !important;
        font-size: 1.8rem !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.75rem !important;
    }

    .upload-hero p {
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
        line-height: 1.7;
    }

    /* ── Feature Grid ── */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-top: 2rem;
    }

    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.2s ease;
    }

    .feature-card:hover {
        border-color: var(--accent-primary);
        box-shadow: var(--glow);
        transform: translateY(-2px);
    }

    .f-icon {
        font-size: 1.5rem;
        display: block;
        margin-bottom: 0.5rem;
    }

    .feature-card b {
        color: var(--text-primary) !important;
        font-size: 0.9rem;
        display: block;
        margin-bottom: 0.25rem;
    }

    .feature-card p {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        margin: 0 !important;
        line-height: 1.5;
    }

    /* ── Metric Cards ── */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
    }

    .metric-card.blue::before { background: linear-gradient(90deg, var(--accent-primary), transparent); }
    .metric-card.purple::before { background: linear-gradient(90deg, var(--accent-secondary), transparent); }
    .metric-card.green::before { background: linear-gradient(90deg, var(--accent-green), transparent); }
    .metric-card.amber::before { background: linear-gradient(90deg, var(--accent-amber), transparent); }

    .metric-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.4rem;
        font-family: var(--font-mono);
    }

    .metric-value {
        font-family: var(--font-display);
        font-size: 1.8rem;
        color: var(--text-primary);
        font-weight: 700;
        line-height: 1;
    }

    .metric-sub {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.3rem;
    }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1.75rem 0 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border);
    }

    .section-header h3 {
        font-family: var(--font-display) !important;
        font-size: 0.85rem !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 0 !important;
    }

    .section-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: var(--accent-primary);
        box-shadow: 0 0 8px var(--accent-primary);
        flex-shrink: 0;
    }

    /* ── Insight Cards ── */
    .insight-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid var(--accent-primary);
        transition: all 0.2s ease;
    }

    .insight-card:hover {
        border-left-color: var(--accent-secondary);
        background: var(--bg-card-hover);
    }

    .insight-card.warning {
        border-left-color: var(--accent-amber);
    }

    .insight-card.success {
        border-left-color: var(--accent-green);
    }

    .insight-card.danger {
        border-left-color: var(--accent-rose);
    }

    .insight-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.3rem;
    }

    .insight-body {
        font-size: 0.8rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* ── Chat Interface ── */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }

    .chat-message {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chat-message.user {
        flex-direction: row-reverse;
    }

    .chat-avatar {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }

    .chat-avatar.ai {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    }

    .chat-avatar.user {
        background: var(--bg-card);
        border: 1px solid var(--border-bright);
    }

    .chat-bubble {
        max-width: 75%;
        padding: 0.9rem 1.1rem;
        border-radius: 12px;
        font-size: 0.88rem;
        line-height: 1.65;
    }

    .chat-bubble.ai {
        background: var(--bg-card);
        border: 1px solid var(--border);
        color: var(--text-primary);
        border-bottom-left-radius: 4px;
    }

    .chat-bubble.user {
        background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,58,237,0.15));
        border: 1px solid rgba(0,212,255,0.3);
        color: var(--text-primary);
        border-bottom-right-radius: 4px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary) !important;
        border-radius: 10px;
        padding: 4px;
        gap: 2px;
        border: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 7px !important;
        font-family: var(--font-sans) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.25rem !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-bright) !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem !important;
    }

    /* ── Inputs ── */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        font-family: var(--font-sans) !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.15) !important;
    }

    /* ── Buttons ── */
    .stButton button {
        background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(124,58,237,0.15)) !important;
        border: 1px solid rgba(0,212,255,0.4) !important;
        color: var(--accent-primary) !important;
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        font-size: 0.85rem !important;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, rgba(0,212,255,0.25), rgba(124,58,237,0.25)) !important;
        border-color: var(--accent-primary) !important;
        box-shadow: var(--glow) !important;
        transform: translateY(-1px) !important;
    }

    /* Primary button */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
        color: white !important;
        border: none !important;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* ── Code Block ── */
    .stCodeBlock {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* ── Plotly Charts ── */
    .js-plotly-plot {
        border-radius: 10px;
        overflow: hidden;
    }

    /* ── Status Badge ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: var(--font-mono);
    }

    .status-badge.online {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: var(--accent-green);
    }

    .status-badge.dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: var(--accent-green);
        animation: blink 1.5s ease infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* ── SQL Console ── */
    .sql-output {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem;
        font-family: var(--font-mono);
        font-size: 0.82rem;
        color: var(--text-secondary);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-primary); }

    /* ── Streamlit overrides ── */
    .stSpinner { color: var(--accent-primary) !important; }
    .stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.3) !important; }
    .stInfo { background: rgba(0,212,255,0.08) !important; border: 1px solid rgba(0,212,255,0.25) !important; }
    .stWarning { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.25) !important; }
    .stError { background: rgba(244,63,94,0.1) !important; border: 1px solid rgba(244,63,94,0.3) !important; }

    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        color: var(--text-primary) !important;
    }

    hr { border-color: var(--border) !important; }

    /* hide default streamlit menu */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)