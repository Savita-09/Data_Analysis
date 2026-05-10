import streamlit as st
import pandas as pd
import numpy as np


def render_explorer():
    df = st.session_state.df

    st.markdown("""
    <div class="section-header">
        <div class="section-dot"></div>
        <h3>Data Explorer</h3>
    </div>
    """, unsafe_allow_html=True)

    exp_tabs = st.tabs(["📋 Raw Data", "📊 Statistics", "🔍 Filter & Search", "📝 Column Profile"])

    # Raw Data 
    with exp_tabs[0]:
        col1, col2, col3 = st.columns(3)
        with col1:
            n_rows = st.slider("Rows to show", 10, min(500, len(df)), 50)
        with col2:
            sort_col = st.selectbox("Sort by", ["(none)"] + df.columns.tolist())
        with col3:
            sort_dir = st.selectbox("Direction", ["Ascending", "Descending"])

        display_df = df.copy()
        if sort_col != "(none)":
            display_df = display_df.sort_values(
                sort_col,
                ascending=(sort_dir == "Ascending")
            )

        st.dataframe(
            display_df.head(n_rows),
            use_container_width=True,
            height=400
        )

        col1, col2 = st.columns(2)
        with col1:
            csv = display_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV",
                data=csv,
                file_name="filtered_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col2:
            st.markdown(
                f'<div style="color:#8b9cc8; font-size:0.8rem; text-align:center; padding-top:0.6rem;">'
                f'Showing {min(n_rows, len(df)):,} of {len(df):,} rows</div>',
                unsafe_allow_html=True
            )

    # Statistics 
    with exp_tabs[1]:
        numeric = df.select_dtypes(include='number')
        if len(numeric.columns) > 0:
            st.markdown("**Numeric Columns**")
            desc = numeric.describe().T
            desc["skew"] = numeric.skew()
            desc["kurtosis"] = numeric.kurtosis()
            desc["missing"] = df.isnull().sum()[numeric.columns]
            desc["missing_pct"] = (desc["missing"] / len(df) * 100).round(2)
            st.dataframe(desc.round(4), use_container_width=True)

        cat_cols = df.select_dtypes(include='object').columns
        if len(cat_cols) > 0:
            st.markdown("**Categorical Columns**")
            cat_stats = []
            for col in cat_cols:
                cat_stats.append({
                    "Column": col,
                    "Unique Values": df[col].nunique(),
                    "Most Common": str(df[col].mode()[0]) if len(df[col].mode()) > 0 else "N/A",
                    "Most Common Count": int(df[col].value_counts().iloc[0]) if len(df[col]) > 0 else 0,
                    "Missing": int(df[col].isnull().sum()),
                    "Missing %": round(df[col].isnull().mean() * 100, 2),
                })
            st.dataframe(pd.DataFrame(cat_stats), use_container_width=True, hide_index=True)

    # Filter & Search 
    with exp_tabs[2]:
        st.markdown("**Filter Data**")
        filtered_df = df.copy()

        filter_col = st.selectbox("Filter column", df.columns.tolist(), key="filter_col")
        dtype = str(df[filter_col].dtype)

        if dtype in ["int64", "float64"]:
            min_val = float(df[filter_col].min())
            max_val = float(df[filter_col].max())
            if min_val < max_val:
                range_val = st.slider(
                    f"Range for {filter_col}",
                    min_val, max_val,
                    (min_val, max_val),
                    key="filter_range"
                )
                filtered_df = filtered_df[
                    (filtered_df[filter_col] >= range_val[0]) &
                    (filtered_df[filter_col] <= range_val[1])
                ]
        else:
            unique_vals = df[filter_col].dropna().unique()[:100]
            selected_vals = st.multiselect(
                f"Select values for {filter_col}",
                options=unique_vals,
                default=list(unique_vals[:5]),
                key="filter_vals"
            )
            if selected_vals:
                filtered_df = filtered_df[filtered_df[filter_col].isin(selected_vals)]

        # Search
        search_term = st.text_input("🔍 Search in all text columns", placeholder="Type to search...")
        if search_term:
            mask = pd.Series([False] * len(filtered_df))
            for col in filtered_df.select_dtypes(include='object').columns:
                mask |= filtered_df[col].astype(str).str.contains(
                    search_term, case=False, na=False
                )
            filtered_df = filtered_df[mask]

        st.markdown(
            f'<div style="color:#10b981; font-size:0.8rem; margin-bottom:0.5rem;">'
            f'✓ {len(filtered_df):,} rows match filters</div>',
            unsafe_allow_html=True
        )
        st.dataframe(filtered_df.head(200), use_container_width=True, height=350)

    # Column Profile 
    with exp_tabs[3]:
        profile_col = st.selectbox("Select column to profile", df.columns.tolist(), key="profile_col")

        col = df[profile_col]
        dtype = str(col.dtype)

        c1, c2 = st.columns(2)
        with c1:
            info = {
                "Data Type": dtype,
                "Total Values": f"{len(col):,}",
                "Non-Null": f"{col.count():,}",
                "Missing": f"{col.isnull().sum():,} ({col.isnull().mean()*100:.1f}%)",
                "Unique Values": f"{col.nunique():,}",
                "Duplicate Rate": f"{(1 - col.nunique()/col.count())*100:.1f}%",
            }

            if dtype in ["int64", "float64"]:
                info.update({
                    "Mean": f"{col.mean():.4f}",
                    "Std Dev": f"{col.std():.4f}",
                    "Min": f"{col.min():.4f}",
                    "Max": f"{col.max():.4f}",
                    "Skewness": f"{col.skew():.4f}",
                    "Kurtosis": f"{col.kurtosis():.4f}",
                    "Median": f"{col.median():.4f}",
                    "Q1 (25%)": f"{col.quantile(0.25):.4f}",
                    "Q3 (75%)": f"{col.quantile(0.75):.4f}",
                })

            for k, v in info.items():
                st.markdown(
                    f'<div style="display:flex; justify-content:space-between; '
                    f'padding:0.35rem 0; border-bottom:1px solid #1e2d45; font-size:0.82rem;">'
                    f'<span style="color:#8b9cc8;">{k}</span>'
                    f'<span style="color:#f0f4ff; font-family:monospace;">{v}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        with c2:
            if dtype in ["int64", "float64"]:
                from utils.charts import distribution_chart
                st.plotly_chart(
                    distribution_chart(df, profile_col),
                    use_container_width=True
                )
            else:
                from utils.charts import bar_chart
                st.plotly_chart(
                    bar_chart(df, profile_col, top_n=10),
                    use_container_width=True
                )