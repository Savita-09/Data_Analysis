import streamlit as st
import pandas as pd
import numpy as np
from utils.charts import (
    correlation_heatmap, distribution_chart, bar_chart,
    missing_values_chart, numeric_overview_grid, pie_chart,
    scatter_plot, box_plot, outlier_chart
)


def render_dashboard():
    df = st.session_state.df
    agent = st.session_state.agent

    # Metric Row 
    numeric = df.select_dtypes(include='number')
    missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
    dup_count = df.duplicated().sum()

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card blue">
            <div class="metric-label">Total Records</div>
            <div class="metric-value">{df.shape[0]:,}</div>
            <div class="metric-sub">{df.shape[1]} columns</div>
        </div>
        <div class="metric-card purple">
            <div class="metric-label">Numeric Cols</div>
            <div class="metric-value">{len(numeric.columns)}</div>
            <div class="metric-sub">{len(df.select_dtypes(include='object').columns)} categorical</div>
        </div>
        <div class="metric-card {'amber' if missing_pct > 5 else 'green'}">
            <div class="metric-label">Data Quality</div>
            <div class="metric-value">{100 - missing_pct:.1f}%</div>
            <div class="metric-sub">{df.isnull().sum().sum():,} missing cells</div>
        </div>
        <div class="metric-card {'amber' if dup_count > 0 else 'green'}">
            <div class="metric-label">Duplicates</div>
            <div class="metric-value">{dup_count:,}</div>
            <div class="metric-sub">{'⚠ needs cleaning' if dup_count > 0 else '✓ none found'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Auto Generate Insights 
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="section-header">
            <div class="section-dot"></div>
            <h3>AI-Generated Insights</h3>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🤖 Run Analysis", use_container_width=True):
            with st.spinner("Agent analyzing your data..."):
                insights = agent.generate_insights()
                st.session_state.insights = insights
            st.rerun()

    if st.session_state.insights:
        cols = st.columns(2)
        for idx, insight in enumerate(st.session_state.insights):
            card_type = insight.get("type", "info")
            with cols[idx % 2]:
                cat_icon = {
                    "quality": "🔍", "distribution": "📊", "correlation": "🔗",
                    "outlier": "⚠️", "trend": "📈", "recommendation": "💡"
                }.get(insight.get("category", ""), "💡")
                st.markdown(f"""
                <div class="insight-card {card_type}">
                    <div class="insight-title">{cat_icon} {insight.get('title', '')}</div>
                    <div class="insight-body">{insight.get('body', '')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 Click **Run Analysis** to generate AI-powered insights from your data.")

    # Visualizations 
    st.markdown("""
    <div class="section-header">
        <div class="section-dot"></div>
        <h3>Visualizations</h3>
    </div>
    """, unsafe_allow_html=True)

    viz_tabs = st.tabs([
        "📊 Overview", "📈 Distributions", "🔗 Correlations",
        "🔍 Outliers", "🥧 Categories", "✏️ Custom"
    ])

    # Overview Tab 
    with viz_tabs[0]:
        if len(numeric.columns) > 0:
            fig = numeric_overview_grid(df, max_cols=8)
            if fig:
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key="overview_numeric_grid"
                )

        missing_fig = missing_values_chart(df)
        if missing_fig:
            st.plotly_chart(
                missing_fig,
                use_container_width=True,
                key="overview_missing_values"
            )
            
        else:
            st.success("✅ No missing values in this dataset.")

    # Distributions Tab 
    with viz_tabs[1]:
        if len(numeric.columns) == 0:
            st.warning("No numeric columns found for distribution analysis.")
        else:
            col_select = st.selectbox(
                "Select column", numeric.columns.tolist(),
                key="dist_col"
            )
            if col_select:
                c1, c2 = st.columns(2)
                with c1:
                    dist_fig = distribution_chart(df, col_select)
                    if dist_fig:
                        st.plotly_chart(
                            dist_fig,
                            use_container_width=True,
                            key=f"dist_chart_{col_select}"
                        )
                        
                with c2:
                    box_fig = box_plot(df, col_select)
                    if box_fig:
                        st.plotly_chart(
                            box_fig,
                            use_container_width=True,
                            key=f"dist_box_{col_select}"
                        )

                # Stats summary
                s = df[col_select].describe()
                st.markdown(f"""
                <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem; margin-top:1rem;">
                    {''.join([
                        f'<div style="background:#141d2e; border:1px solid #1e2d45; border-radius:8px; padding:0.75rem; text-align:center;">'
                        f'<div style="font-size:0.7rem; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em;">{k}</div>'
                        f'<div style="font-family:monospace; font-size:1rem; color:#00d4ff; margin-top:0.2rem;">{v:.3f}</div>'
                        f'</div>'
                        for k, v in [("mean", s["mean"]), ("std", s["std"]),
                                      ("min", s["min"]), ("max", s["max"])]
                    ])}
                </div>
                """, unsafe_allow_html=True)

    # Correlations Tab 
    with viz_tabs[2]:
        if len(numeric.columns) < 2:
            st.warning("Need at least 2 numeric columns for correlation analysis.")
        else:
            heatmap = correlation_heatmap(df)
            if heatmap:
                st.plotly_chart(
                    heatmap,
                    use_container_width=True,
                    key="correlation_heatmap"
                )

            # Top correlations table
            corr = numeric.corr().abs()
            pairs = []
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    pairs.append({
                        "Column A": corr.columns[i],
                        "Column B": corr.columns[j],
                        "Correlation": round(corr.iloc[i, j], 4),
                        "Strength": (
                            "🔴 Strong" if corr.iloc[i, j] > 0.7
                            else "🟡 Moderate" if corr.iloc[i, j] > 0.4
                            else "🟢 Weak"
                        )
                    })
            pairs.sort(key=lambda x: x["Correlation"], reverse=True)
            if pairs:
                st.dataframe(
                    pd.DataFrame(pairs[:15]),
                    use_container_width=True,
                    hide_index=True
                )

    # Outliers Tab
    with viz_tabs[3]:
        if len(numeric.columns) == 0:
            st.warning("No numeric columns for outlier analysis.")
        else:
            out_col = st.selectbox("Select column", numeric.columns.tolist(), key="out_col")
            if out_col:
                col1, col2 = st.columns(2)
                with col1:
                    outlier_fig = outlier_chart(df, out_col)
                    if outlier_fig:
                        st.plotly_chart(
                            outlier_fig,
                            use_container_width=True,
                            key=f"outlier_chart_{out_col}"
                        )
                with col2:
                    # IQR-based outlier count
                    Q1 = df[out_col].quantile(0.25)
                    Q3 = df[out_col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = df[(df[out_col] < Q1 - 1.5 * IQR) |
                                  (df[out_col] > Q3 + 1.5 * IQR)]
                    st.markdown(f"""
                    <div class="insight-card {'warning' if len(outliers) > 0 else 'success'}">
                        <div class="insight-title">
                            {'⚠️' if len(outliers) > 0 else '✅'} IQR Outlier Detection
                        </div>
                        <div class="insight-body">
                            Found <b>{len(outliers):,}</b> outliers ({len(outliers)/len(df)*100:.1f}%)<br>
                            IQR Range: [{Q1:.3f}, {Q3:.3f}]<br>
                            Lower fence: {Q1 - 1.5*IQR:.3f}<br>
                            Upper fence: {Q3 + 1.5*IQR:.3f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if len(outliers) > 0:
                        st.dataframe(
                            outliers[[out_col]].head(20),
                            use_container_width=True,
                            hide_index=True
                        )

    # Categories Tab
    with viz_tabs[4]:
        cat_cols = df.select_dtypes(include='object').columns.tolist()
        if not cat_cols:
            st.warning("No categorical columns found.")
        else:
            cat_col = st.selectbox("Select column", cat_cols, key="cat_col")
            if cat_col:
                c1, c2 = st.columns(2)
                with c1:
                    bar_fig = bar_chart(df, cat_col)
                    if bar_fig:
                        st.plotly_chart(
                            bar_fig,
                            use_container_width=True,
                            key=f"category_bar_{cat_col}"
                        )
                with c2:
                    pie_fig = pie_chart(df, cat_col)
                    if pie_fig:
                        st.plotly_chart(
                            pie_fig,
                            use_container_width=True,
                            key=f"category_pie_{cat_col}"
                        )

    # Custom Chart Tab
    with viz_tabs[5]:
        st.markdown("**Build a custom chart**")
        col1, col2, col3 = st.columns(3)
        with col1:
            chart_type = st.selectbox(
                "Chart type",
                ["Scatter", "Line", "Bar", "Distribution", "Box"],
                key="custom_type"
            )
        with col2:
            x_col = st.selectbox(
                "X axis",
                df.columns.tolist(),
                key="custom_x"
            )
        with col3:
            y_options = ["(none)"] + df.select_dtypes(include='number').columns.tolist()
            y_col = st.selectbox("Y axis", y_options, key="custom_y")

        color_options = ["(none)"] + df.select_dtypes(include='object').columns.tolist()
        color_col = st.selectbox("Color by (optional)", color_options, key="custom_color")
        color_col = None if color_col == "(none)" else color_col
        y_col = None if y_col == "(none)" else y_col

        if st.button("🎨 Generate Chart", use_container_width=True):
            with st.spinner("Building chart..."):
                fig = None
                if chart_type == "Scatter" and y_col:
                    fig = scatter_plot(df, x_col, y_col, color_col)
                elif chart_type == "Line" and y_col:
                    from utils.charts import line_chart
                    fig = line_chart(df, x_col, y_col)
                elif chart_type == "Bar":
                    fig = bar_chart(df, x_col)
                elif chart_type == "Distribution":
                    if x_col in df.select_dtypes(include='number').columns:
                        fig = distribution_chart(df, x_col)
                elif chart_type == "Box":
                    if x_col in df.select_dtypes(include='number').columns:
                        fig = box_plot(df, x_col, color_col)

                if fig:
                    custom_key = f"custom_{chart_type}_{x_col}_{y_col}_{color_col}"
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key=custom_key
                    )
                else:
                    st.warning("Please select appropriate columns for this chart type.")