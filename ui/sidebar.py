import streamlit as st
import pandas as pd


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.5rem 0 1.5rem; text-align:center;">
            <div style="font-size:1.8rem; margin-bottom:0.3rem;">🧠</div>
            <div style="font-family:'Space Mono',monospace; font-size:0.85rem;
                        color:#00d4ff; letter-spacing:0.1em;">DataAnalysis Agent</div>
            <div class="status-badge online" style="margin-top:0.5rem; display:inline-flex;">
                <span class="dot"></span> ACTIVE
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        #  API Key 
        st.markdown("**🔑 Groq API Key**")
        api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-ant-...",
            label_visibility="collapsed",
            help="Required for AI-powered insights and chat"
        )
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            if st.session_state.agent:
                st.session_state.agent.api_key = api_key

        if st.session_state.api_key:
            st.markdown('<p style="color:#10b981; font-size:0.75rem;">✓ API key set</p>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#f59e0b; font-size:0.75rem;">⚠ Add key for AI features</p>',
                        unsafe_allow_html=True)

        st.divider()

        # Dataset Information
        if st.session_state.df is not None:
            df = st.session_state.df
            st.markdown("**📋 Dataset Info**")

            info_items = [
                ("File", st.session_state.get("file_name", "dataset.csv")),
                ("Rows", f"{df.shape[0]:,}"),
                ("Columns", str(df.shape[1])),
                ("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB"),
                ("Numeric", str(len(df.select_dtypes(include='number').columns))),
                ("Categorical", str(len(df.select_dtypes(include='object').columns))),
                ("Missing", f"{df.isnull().sum().sum():,} cells"),
            ]

            for label, val in info_items:
                st.markdown(
                    f'<div style="display:flex; justify-content:space-between; '
                    f'padding:0.3rem 0; border-bottom:1px solid #1e2d45; font-size:0.78rem;">'
                    f'<span style="color:#8b9cc8;">{label}</span>'
                    f'<span style="color:#f0f4ff; font-family:monospace;">{val}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.divider()

            # Column Browser 
            st.markdown("**🗂 Columns**")
            for col in df.columns:
                dtype = str(df[col].dtype)
                icon = "🔢" if dtype in ["int64", "float64"] else "📝" if dtype == "object" else "📅"
                null_pct = df[col].isnull().mean() * 100
                null_str = f"  ⚠ {null_pct:.0f}% null" if null_pct > 0 else ""
                st.markdown(
                    f'<div style="font-size:0.75rem; padding:0.2rem 0; color:#8b9cc8;">'
                    f'{icon} <b style="color:#c4d4f0;">{col}</b>'
                    f'<span style="font-family:monospace; color:#4a5568;"> {dtype}{null_str}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.divider()

            # Actions 
            st.markdown("**⚡ Actions**")
            if st.button("🔄 Load New Dataset", use_container_width=True):
                st.session_state.df = None
                st.session_state.agent = None
                st.session_state.chat_history = []
                st.session_state.insights = []
                st.rerun()

            if st.button("🗑 Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

            if st.button("📥 Export Insights", use_container_width=True):
                if st.session_state.insights:
                    insight_text = "\n\n".join(
                        [f"## {i['title']}\n{i['body']}"
                         for i in st.session_state.insights]
                    )
                    st.download_button(
                        "Download .md",
                        data=insight_text,
                        file_name="insights.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                else:
                    st.info("Run analysis first to generate insights.")

        else:
            st.markdown("""
            <div style="color:#4a5568; font-size:0.8rem; text-align:center; padding:1rem 0;">
                Upload a CSV to get started
            </div>
            """, unsafe_allow_html=True)

        # Footer 
        st.markdown("""
        <div style="position:absolute; bottom:1rem; left:0; right:0; text-align:center;
                    font-size:0.7rem; color:#2a3f60; font-family:monospace;">
        </div>
        """, unsafe_allow_html=True)