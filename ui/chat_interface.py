import streamlit as st
import pandas as pd


SUGGESTED_QUESTIONS = [
    "What are the key statistics for this dataset?",
    "Which columns have missing values and how many?",
    "What are the strongest correlations in this data?",
    "Are there any outliers I should be aware of?",
    "What patterns do you see in the data?",
    "Give me actionable recommendations based on this data.",
    "Write a SQL query to find the top 10 rows by the highest numeric value.",
    "Summarize this dataset in 3 bullet points.",
]


def render_chat():
    agent = st.session_state.agent

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1.5rem;">
            <div style="font-size:2rem; margin-bottom:0.5rem;">💬</div>
            <h3 style="font-family:'Space Mono',monospace; color:#f0f4ff; font-size:1.1rem;">
                Ask anything about your data
            </h3>
            <p style="color:#8b9cc8; font-size:0.85rem;">
                The AI agent will analyze your dataset and answer.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**💡 Suggested questions:**")
        cols = st.columns(2)
        for idx, q in enumerate(SUGGESTED_QUESTIONS):
            with cols[idx % 2]:
                if st.button(f"→ {q}", key=f"suggest_{idx}", use_container_width=True):
                    _process_message(q, agent)
                    st.rerun()

    # Chat History 
    for msg in st.session_state.chat_history:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="chat-avatar user">👤</div>
                <div class="chat-bubble user">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Process markdown in response
            response_text = content.get("response", "")
            st.markdown(f"""
            <div class="chat-message">
                <div class="chat-avatar ai">🧠</div>
                <div class="chat-bubble ai" style="max-width:80%;">
            """, unsafe_allow_html=True)
            st.markdown(response_text)
            st.markdown("</div></div>", unsafe_allow_html=True)

            # Show SQL result if any
            if content.get("sql"):
                with st.expander(f"🔍 SQL Generated", expanded=False):
                    st.code(content["sql"], language="sql")
                    if content.get("sql_result") is not None:
                        st.dataframe(
                            content["sql_result"].head(50),
                            use_container_width=True,
                            hide_index=True
                        )

    # Input Area 
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns([8, 1])
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask anything about your data... (e.g. 'What are the key trends?')",
                label_visibility="collapsed",
                key="chat_input"
            )
        with col2:
            send_btn = st.button("Send →", use_container_width=True, type="primary")

    if send_btn and user_input.strip():
        with st.spinner("🧠 Agent thinking..."):
            _process_message(user_input.strip(), agent)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def _process_message(user_message: str, agent):
    """Add user message and get AI response."""
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_message
    })

    if agent is None:
        st.error("Agent is not initialized.")
        return

    result = agent.chat(user_message)
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result
    })