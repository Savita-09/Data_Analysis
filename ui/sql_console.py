import streamlit as st
import pandas as pd


SAMPLE_QUERIES = [
    ("Count all rows", "SELECT COUNT(*) as total_rows FROM {table}"),
    ("Top 10 rows", "SELECT * FROM {table} LIMIT 10"),
    ("Column names & types", "PRAGMA table_info({table})"),
    ("Find duplicates", "SELECT *, COUNT(*) as cnt FROM {table} GROUP BY {table}.rowid HAVING cnt > 1"),
    ("Missing value check", "SELECT COUNT(*) as total, {num_col} FROM {table} WHERE {num_col} IS NULL"),
    ("Group & aggregate", "SELECT {cat_col}, COUNT(*) as count, AVG({num_col}) as avg_value FROM {table} GROUP BY {cat_col} ORDER BY count DESC LIMIT 15"),
]


def render_sql_console():
    df = st.session_state.df
    db = st.session_state.db_manager
    agent = st.session_state.agent
    table_name = st.session_state.get("table_name", "dataset")

    st.markdown("""
    <div class="section-header">
        <div class="section-dot"></div>
        <h3>SQL Console</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="background:#141d2e; border:1px solid #1e2d45; border-radius:8px;
                    padding:0.75rem 1rem; margin-bottom:1rem; font-size:0.82rem; font-family:monospace;">
            <span style="color:#4a5568;">Active table:</span>
            <span style="color:#00d4ff; margin-left:0.5rem;">{table_name}</span>
            <span style="color:#4a5568; margin-left:1.5rem;">Rows:</span>
            <span style="color:#10b981; margin-left:0.5rem;">{len(df):,}</span>
            <span style="color:#4a5568; margin-left:1.5rem;">Cols:</span>
            <span style="color:#10b981; margin-left:0.5rem;">{df.shape[1]}</span>
        </div>
        """, unsafe_allow_html=True)

    # Natural Language to SQL 
    #st.markdown("**🤖 Natural Language → SQL**")
    #col1, col2 = st.columns([4, 1])
    #with col1:
     #   nl_query = st.text_input(
      #      "NL Query",
       #     placeholder='e.g. "Show me the top 5 customers by total spend"',
        #    label_visibility="collapsed",
         #   key="nl_query_input"
        #)
    #with col2:
     #   gen_btn = st.button("Generate SQL", use_container_width=True, key="gen_sql_btn")

    #if gen_btn and nl_query:
     #   with st.spinner("Generating SQL..."):
      #      generated_sql = agent.generate_sql(nl_query)
       #     st.session_state.current_sql = generated_sql

    # SQL Editor 
    st.markdown("**📝 SQL Editor**")

    # Populate with sample queries
    num_cols = df.select_dtypes(include='number').columns
    cat_cols = df.select_dtypes(include='object').columns
    num_col = num_cols[0] if len(num_cols) > 0 else "value"
    cat_col = cat_cols[0] if len(cat_cols) > 0 else "category"

    col1, col2 = st.columns([3, 1])
    with col2:
        template_names = [q[0] for q in SAMPLE_QUERIES]
        selected_template = st.selectbox(
            "Load template",
            ["(choose)"] + template_names,
            key="sql_template"
        )
        if selected_template != "(choose)":
            for name, query in SAMPLE_QUERIES:
                if name == selected_template:
                    sql_template = query.format(
                        table=table_name,
                        num_col=num_col,
                        cat_col=cat_col
                    )
                    st.session_state.current_sql = sql_template
                    break

    with col1:
        default_sql = st.session_state.get(
            "current_sql",
            f"SELECT * FROM {table_name} LIMIT 20"
        )
        sql_input = st.text_area(
            "SQL",
            value=default_sql,
            height=140,
            label_visibility="collapsed",
            key="sql_editor"
        )

    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        run_btn = st.button("▶ Run Query", use_container_width=True, type="primary")
    with col2:
        clear_btn = st.button("🗑 Clear", use_container_width=True)

    if clear_btn:
        st.session_state.current_sql = f"SELECT * FROM {table_name} LIMIT 20"
        st.rerun()

    # Execute 
    if run_btn and sql_input.strip():
        with st.spinner("Executing query..."):
            result_df, error = db.execute_query(sql_input)

        if error:
            st.error(f"❌ SQL Error: {error}")
        elif result_df is not None:
            st.success(f"✅ Query returned {len(result_df):,} rows × {result_df.shape[1]} columns")

            # Display results
            st.dataframe(result_df, use_container_width=True, height=350)

            # Download results
            col1, col2 = st.columns([1, 4])
            with col1:
                csv = result_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Export CSV",
                    data=csv,
                    file_name="query_result.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            # Visualize if appropriate
            if len(result_df) > 1 and len(result_df.select_dtypes(include='number').columns) > 0:
                with st.expander("📊 Visualize Results"):
                    num_result_cols = result_df.select_dtypes(include='number').columns.tolist()
                    text_result_cols = result_df.select_dtypes(include='object').columns.tolist()

                    vc1, vc2 = st.columns(2)
                    with vc1:
                        viz_type = st.selectbox(
                            "Chart type",
                            ["Bar", "Line", "Scatter"],
                            key="sql_viz_type"
                        )
                    with vc2:
                        y_col_viz = st.selectbox(
                            "Y axis (numeric)",
                            num_result_cols,
                            key="sql_viz_y"
                        )

                    if text_result_cols and viz_type == "Bar":
                        x_col_viz = st.selectbox(
                            "X axis",
                            text_result_cols,
                            key="sql_viz_x"
                        )
                        from utils.charts import apply_theme, DARK_THEME
                        import plotly.express as px
                        fig = px.bar(
                            result_df.head(30),
                            x=x_col_viz, y=y_col_viz,
                            color_discrete_sequence=DARK_THEME["colorway"]
                        )
                        apply_theme(fig)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    if text_result_cols and viz_type == "line":
                        x_col_viz = st.selectbox(
                            "X axis",
                            text_result_cols,
                            key="sql_viz_x"
                        )
                        from utils.charts import apply_theme, DARK_THEME
                        import plotly.express as px
                        fig = px.line(
                            result_df.head(30),
                            x=x_col_viz, y=y_col_viz,
                            color_discrete_sequence=DARK_THEME["colorway"]
                        )
                        apply_theme(fig)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    if text_result_cols and viz_type == "Scatter":
                        x_col_viz = st.selectbox(
                            "X axis",
                            text_result_cols,
                            key="sql_viz_x"
                        )
                        from utils.charts import apply_theme, DARK_THEME
                        import plotly.express as px
                        fig = px.scatter(
                            result_df.head(30),
                            x=x_col_viz, y=y_col_viz,
                            color_discrete_sequence=DARK_THEME["colorway"]
                        )
                        apply_theme(fig)
                        st.plotly_chart(fig, use_container_width=True)

    # Schema Reference 
    with st.expander("📋 Schema Reference"):
        schema_data = []
        for col in df.columns:
            schema_data.append({
                "Column": col,
                "Type": str(df[col].dtype),
                "Non-Null": f"{df[col].count():,}",
                "Unique": f"{df[col].nunique():,}",
                "Sample": str(df[col].dropna().iloc[0]) if df[col].count() > 0 else "N/A"
            })
        st.dataframe(
            pd.DataFrame(schema_data),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(f"""
        <div style="font-family:monospace; font-size:0.78rem; color:#4a5568; margin-top:0.5rem;">
            Table: <span style="color:#00d4ff;">{table_name}</span>
        </div>
        """, unsafe_allow_html=True)
