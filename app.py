import streamlit as st
import pandas as pd
import os
from pathlib import Path


st.set_page_config(
    page_title="Data Analysis System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


from ui.styles import apply_styles
from ui.sidebar import render_sidebar
from ui.dashboard import render_dashboard
from ui.chat_interface import render_chat
from database.db_manager import DatabaseManager
from agent.analysis_agent import DataAnalysisAgent

apply_styles()


if "df" not in st.session_state:
    st.session_state.df = None
if "agent" not in st.session_state:
    st.session_state.agent = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "insights" not in st.session_state:
    st.session_state.insights = []
if "db_manager" not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "dashboard"


col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.markdown("""
    <div class="app-header">
        <div class="header-icon">🧠</div>
        <h1 class="app-title">Data Analysis<span class="accent"><br>Agent</span></h1>
    </div>
    """, unsafe_allow_html=True)

render_sidebar()


if st.session_state.df is None:
    st.markdown("""
    <div class="upload-zone-wrapper">
        <div class="upload-hero">
            <div class="hero-glyph">⬡</div>
            <h2>Drop your data.</h2>
            <p>Upload a CSV file to activate the AI analysis agent. It will autonomously explore,
            visualize, and surface insights from your dataset.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader(
            "Upload CSV File",
            type=["csv"],
            help="Supports CSV files up to 200MB",
            label_visibility="collapsed"
        )

        if uploaded_file:
            with st.spinner("🔍 Reading and profiling your data..."):
                df = pd.read_csv(uploaded_file)
                st.session_state.df = df
                st.session_state.file_name = uploaded_file.name
                # Store in DB
                table_name = Path(uploaded_file.name).stem.replace(" ", "_").lower()
                st.session_state.table_name = table_name
                st.session_state.db_manager.store_dataframe(df, table_name)
                # Initialize agent
                st.session_state.agent = DataAnalysisAgent(
                    df=df,
                    api_key=st.session_state.api_key,
                    db_manager=st.session_state.db_manager,
                    table_name=table_name
                )
            st.success(f"✅ Loaded **{uploaded_file.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")
            st.rerun()

        st.markdown("""
        <div class="feature-grid">
            <div class="feature-card">
                <span class="f-icon">🤖</span>
                <b>Agentic Analysis</b>
                <p>AI autonomously plans and executes multi-step analysis workflows</p>
            </div>
            <div class="feature-card">
                <span class="f-icon">📊</span>
                <b>Auto Dashboards</b>
                <p>Intelligent chart selection based on data types and distributions</p>
            </div>
            <div class="feature-card">
                <span class="f-icon">🗄️</span>
                <b>SQL Powered</b>
                <p>Data stored in MySQL/SQLite with natural language to SQL translation</p>
            </div>
            <div class="feature-card">
                <span class="f-icon">💬</span>
                <b>Chat Interface</b>
                <p>Ask questions and get answers with visualizations</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    # Main App with Data Loaded
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊  Dashboard",
        "💬  AI Chat",
        "🔍  Data Explorer",
        "🗄️  SQL Console"
    ])

    with tab1:
        render_dashboard()

    with tab2:
        render_chat()

    with tab3:
        from ui.data_explorer import render_explorer
        render_explorer()

    with tab4:
        from ui.sql_console import render_sql_console
        render_sql_console()