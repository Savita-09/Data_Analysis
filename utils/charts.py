import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


# Plotly theme 
DARK_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(20,29,46,0.6)",
    "font": {"family": "DM Sans, sans-serif", "color": "#8b9cc8", "size": 11},
    "xaxis": {
        "gridcolor": "#1e2d45",
        "linecolor": "#1e2d45",
        "tickcolor": "#4a5568",
        "tickfont": {"size": 10},
    },
    "yaxis": {
        "gridcolor": "#1e2d45",
        "linecolor": "#1e2d45",
        "tickcolor": "#4a5568",
        "tickfont": {"size": 10},
    },
    "colorway": [
        "#00d4ff", "#7c3aed", "#10b981", "#f59e0b",
        "#f43f5e", "#06b6d4", "#8b5cf6", "#34d399",
    ],
}

COLOR_SCALE = [
    [0.0, "#0a0e17"],
    [0.2, "#1e2d45"],
    [0.4, "#2a3f60"],
    [0.6, "#7c3aed"],
    [0.8, "#00d4ff"],
    [1.0, "#f0f4ff"],
]


def apply_theme(fig):
    """Apply DataMind dark theme to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor=DARK_THEME["paper_bgcolor"],
        plot_bgcolor=DARK_THEME["plot_bgcolor"],
        font=DARK_THEME["font"],
        margin={"t": 40, "r": 20, "b": 40, "l": 50},
        legend={
            "bgcolor": "rgba(20,29,46,0.8)",
            "bordercolor": "#1e2d45",
            "borderwidth": 1,
            "font": {"size": 10},
        },
        colorway=DARK_THEME["colorway"],
    )
    fig.update_xaxes(**DARK_THEME["xaxis"])
    fig.update_yaxes(**DARK_THEME["yaxis"])
    return fig


# Individual Chart Functions 

def distribution_chart(df: pd.DataFrame, col: str):
    """Histogram + KDE for a numeric column."""
    fig = px.histogram(
        df, x=col,
        nbins=40,
        marginal="box",
        title=f"Distribution: {col}",
        color_discrete_sequence=["#00d4ff"],
    )
    apply_theme(fig)
    fig.update_traces(
        marker_line_color="#1e2125",
        marker_line_width=0.5,
        opacity=0.85
    )
    return fig


def correlation_heatmap(df: pd.DataFrame):
    """Correlation matrix heatmap for numeric columns."""
    numeric = df.select_dtypes(include='number')
    if len(numeric.columns) < 2:
        return None

    corr = numeric.corr().round(3)
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale=COLOR_SCALE,
        zmin=-1, zmax=1,
        text=corr.values.round(2),
        texttemplate="%{text}",
        textfont={"size": 9},
        hoverongaps=False,
    ))
    fig.update_layout(
        title="Correlation Matrix",
        height=max(350, len(corr.columns) * 50),
    )
    apply_theme(fig)
    return fig


def scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None):
    """Scatter plot with optional color grouping."""
    kwargs = {"x": x_col, "y": y_col, "title": f"{x_col} vs {y_col}"}
    if color_col and color_col in df.columns:
        kwargs["color"] = color_col
    fig = px.scatter(df.sample(min(2000, len(df))), **kwargs,
                     color_discrete_sequence=DARK_THEME["colorway"],
                     opacity=0.7)
    fig.update_traces(marker={"size": 5})
    apply_theme(fig)
    return fig


def bar_chart(df: pd.DataFrame, col: str, top_n: int = 15):
    """Bar chart for categorical column value counts."""
    counts = df[col].value_counts().head(top_n).reset_index()
    counts.columns = [col, "count"]
    fig = px.bar(
        counts, x=col, y="count",
        title=f"Top {top_n} Values: {col}",
        color="count",
        color_continuous_scale=COLOR_SCALE,
    )
    apply_theme(fig)
    fig.update_traces(marker_line_width=0)
    return fig


def line_chart(df: pd.DataFrame, x_col: str, y_col: str):
    """Line chart for time series or ordered data."""
    fig = px.line(
        df, x=x_col, y=y_col,
        title=f"{y_col} over {x_col}",
        color_discrete_sequence=["#00d4ff"],
    )
    apply_theme(fig)
    fig.update_traces(line={"width": 2})
    return fig


def box_plot(df: pd.DataFrame, col: str, group_col: str = None):
    """Box plot for outlier detection."""
    kwargs = {"y": col, "title": f"Box Plot: {col}"}
    if group_col and group_col in df.columns:
        kwargs["x"] = group_col
    fig = px.box(df, **kwargs,
                 color_discrete_sequence=DARK_THEME["colorway"])
    apply_theme(fig)
    return fig


def pie_chart(df: pd.DataFrame, col: str, top_n: int = 8):
    """Pie/donut chart for categorical distribution."""
    counts = df[col].value_counts().head(top_n)
    fig = px.pie(
        values=counts.values,
        names=counts.index,
        title=f"Distribution: {col}",
        hole=0.45,
        color_discrete_sequence=DARK_THEME["colorway"],
    )
    apply_theme(fig)
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont_size=10,
    )
    return fig


def missing_values_chart(df: pd.DataFrame):
    """Bar chart showing missing value percentages."""
    missing = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    missing = missing[missing > 0]
    if len(missing) == 0:
        return None

    fig = px.bar(
        x=missing.index,
        y=missing.values,
        title="Missing Values (%)",
        labels={"x": "Column", "y": "Missing %"},
        color=missing.values,
        color_continuous_scale=[[0, "#10b981"], [0.5, "#f59e0b"], [1, "#f43f5e"]],
    )
    apply_theme(fig)
    fig.update_traces(marker_line_width=0)
    return fig


def outlier_chart(df: pd.DataFrame, col: str):
    """Violin + scatter for outlier visualization."""
    fig = go.Figure()
    fig.add_trace(go.Violin(
        y=df[col].dropna(),
        name=col,
        box_visible=True,
        meanline_visible=True,
        fillcolor="rgba(0,212,255,0.2)",
        line_color="#00d4ff",
        opacity=0.8,
    ))
    fig.update_layout(title=f"Outlier Analysis: {col}", showlegend=False)
    apply_theme(fig)
    return fig


def numeric_overview_grid(df: pd.DataFrame, max_cols: int = 6):
    """Mini histogram grid for all numeric columns."""
    numeric_cols = df.select_dtypes(include='number').columns[:max_cols].tolist()
    if not numeric_cols:
        return None

    n = len(numeric_cols)
    cols_per_row = min(3, n)
    rows = (n + cols_per_row - 1) // cols_per_row

    fig = make_subplots(
        rows=rows, cols=cols_per_row,
        subplot_titles=numeric_cols,
    )

    for idx, col in enumerate(numeric_cols):
        row = idx // cols_per_row + 1
        col_pos = idx % cols_per_row + 1
        fig.add_trace(
            go.Histogram(
                x=df[col].dropna(),
                nbinsx=25,
                name=col,
                marker_color=DARK_THEME["colorway"][idx % len(DARK_THEME["colorway"])],
                showlegend=False,
                opacity=0.85,
            ),
            row=row, col=col_pos,
        )

    fig.update_layout(
        title="Numeric Column Distributions",
        height=260 * rows,
    )
    apply_theme(fig)
    fig.update_annotations(font_size=11, font_color="#8b9cc8")
    return fig