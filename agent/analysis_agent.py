import pandas as pd
import numpy as np
import json
import re
import requests
from typing import Any, Dict, List, Optional
from database.db_manager import DatabaseManager
import os

SYSTEM_PROMPT = """You are DataMind, an expert autonomous data analysis agent.

Your capabilities:
1. Statistical analysis (descriptive stats, correlations, distributions)
2. Data quality assessment (missing values, outliers, data types)
3. Pattern recognition (trends, seasonality, anomalies)
4. Business insight generation (actionable recommendations)
5. SQL query generation for deeper analysis
6. Chart/visualization recommendations

When analyzing data:
- Always provide concrete numbers and percentages
- Highlight the most important findings first
- Suggest actionable next steps
- Identify data quality issues proactively
- Explain technical findings in plain language

Response format for insights: Use JSON when asked for structured output.
For conversational responses: Be concise, clear, and insightful.

IMPORTANT: When generating SQL, always use the exact table name provided.
"""

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_BASE = "https://api.groq.com/openai/v1"


class DataAnalysisAgent:
    """
    Autonomous AI agent for data analysis powered by Groq API
    (OpenAI-compatible endpoint).
    Supports multi-step agentic workflows, SQL generation, and insight synthesis.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        api_key: str,          
        db_manager: DatabaseManager,
        table_name: str,
    ):
        self.df = df
        self.api_key = api_key
        self.db_manager = db_manager
        self.table_name = table_name
        self.conversation_history: List[Dict[str, str]] = []
        self._profile = self._build_profile()

    def _build_profile(self) -> Dict[str, Any]:
        df = self.df
        numeric_cols     = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include="object").columns.tolist()
        datetime_cols    = df.select_dtypes(include="datetime").columns.tolist()

        profile: Dict[str, Any] = {
            "shape":           {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
            "columns":         df.columns.tolist(),
            "dtypes":          {col: str(dtype) for col, dtype in df.dtypes.items()},
            "numeric_cols":    numeric_cols,
            "categorical_cols": categorical_cols,
            "datetime_cols":   datetime_cols,
            "missing": {
                col: int(df[col].isnull().sum())
                for col in df.columns
                if df[col].isnull().sum() > 0
            },
            "sample": df.head(3).to_dict(orient="records"),
        }

        if numeric_cols:
            profile["numeric_stats"] = df[numeric_cols].describe().round(3).to_dict()

        cat_stats: Dict[str, Any] = {}
        for col in categorical_cols[:10]:
            cat_stats[col] = {
                "unique":     int(df[col].nunique()),
                "top_values": df[col].value_counts().head(5).to_dict(),
            }
        profile["categorical_stats"] = cat_stats

        return profile

    # Groq API Call (OpenAI-compatible) 
    def _call_groq(self, messages: List[Dict[str, str]], max_tokens: int = 2048) -> str:
        """
        Call the Groq chat-completions endpoint.

        Groq uses the OpenAI format:
          POST https://api.groq.com/openai/v1/chat/completions
          Body: { model, messages, max_tokens, temperature }
          Response: { choices: [{ message: { content: "..." } }] }

        The system prompt is sent as the FIRST message with role="system".
        """
        if not self.api_key:
            last_user = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"),
                "",
            )
            return self._fallback_response(last_user)


        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

        try:
            resp = requests.post(
                f"{GROQ_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       GROQ_MODEL,
                    "messages":    full_messages,
                    "max_tokens":  max_tokens,
                    "temperature": 0.3,     
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()

            # ✅ OpenAI-compatible response shape
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            detail = e.response.text[:300]
            return f"⚠️ Groq API Error {status}: {detail}"
        except KeyError as e:
            return f"⚠️ Unexpected Groq response shape — missing key: {e}"
        except Exception as e:
            return f"⚠️ Error calling Groq: {str(e)}"

    # Fallback (no API key) 
    def _fallback_response(self, user_message: str) -> str:
        """Local rule-based analysis when no API key is set."""
        df  = self.df
        msg = user_message.lower()

        if any(k in msg for k in ["shape", "size", "rows", "columns"]):
            return (
                f"Dataset has **{df.shape[0]:,} rows** and **{df.shape[1]} columns**. "
                f"Columns: {', '.join(df.columns.tolist())}"
            )

        if "missing" in msg or "null" in msg:
            missing = df.isnull().sum()
            missing = missing[missing > 0]
            if missing.empty:
                return "✅ No missing values found in the dataset."
            report = "\n".join(
                f"- **{col}**: {cnt:,} missing ({cnt / len(df) * 100:.1f}%)"
                for col, cnt in missing.items()
            )
            return f"Missing values found:\n{report}"

        if any(k in msg for k in ["describe", "summary", "statistics"]):
            numeric = df.select_dtypes(include="number")
            if not numeric.empty:
                return f"Statistical summary:\n```\n{numeric.describe().round(2).to_string()}\n```"

        if any(k in msg for k in ["correlation", "corr"]):
            numeric = df.select_dtypes(include="number")
            if len(numeric.columns) >= 2:
                corr = numeric.corr().round(3)
                pairs = [
                    (corr.columns[i], corr.columns[j], corr.iloc[i, j])
                    for i in range(len(corr.columns))
                    for j in range(i + 1, len(corr.columns))
                ]
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                result = "\n".join(
                    f"- {a} ↔ {b}: **{v:.3f}**" for a, b, v in pairs[:5]
                )
                return f"Top correlations:\n{result}"

        cols_preview = ", ".join(df.columns[:8].tolist())
        ellipsis     = " ..." if df.shape[1] > 8 else ""
        return (
            f"ℹ️ *Groq API key not set — showing local analysis.*\n\n"
            f"Dataset: **{df.shape[0]:,}** rows × **{df.shape[1]}** columns.\n"
            f"Columns: {cols_preview}{ellipsis}"
        )

    # Context Builder 
    def _build_context(self) -> str:
        p = self._profile
        return (
            f"DATASET PROFILE:\n"
            f"- Table name (for SQL): {self.table_name}\n"
            f"- Shape: {p['shape']['rows']:,} rows × {p['shape']['cols']} columns\n"
            f"- Numeric columns: {', '.join(p['numeric_cols']) or 'none'}\n"
            f"- Categorical columns: {', '.join(p['categorical_cols']) or 'none'}\n"
            f"- Datetime columns: {', '.join(p['datetime_cols']) or 'none'}\n"
            f"- Missing data: {json.dumps(p['missing'])}\n"
            f"- Sample rows: {json.dumps(p['sample'][:2], default=str)}\n"
        )

    # Chat 
    def chat(self, user_message: str) -> Dict[str, Any]:
        """Process a user question; return answer + optional SQL + SQL result."""
        context      = self._build_context()
        full_message = f"{context}\n\nUser question: {user_message}"

        self.conversation_history.append({"role": "user", "content": full_message})

        # Keep last 10 turns to stay within context limits
        messages = self.conversation_history[-10:]

        response_text = self._call_groq(messages)
        self.conversation_history.append({"role": "assistant", "content": response_text})

        # Extract SQL block if present
        sql_match = re.search(r"```sql\n(.*?)\n```", response_text, re.DOTALL)
        sql_query = sql_match.group(1).strip() if sql_match else None

        sql_result = None
        if sql_query:
            sql_result, err = self.db_manager.execute_query(sql_query)
            if err:
                sql_result = None

        return {
            "response":   response_text,
            "sql":        sql_query,
            "sql_result": sql_result,
        }

    # Auto Insights 
    def generate_insights(self) -> List[Dict[str, str]]:
        """Run autonomous multi-step analysis; return 6 structured insights."""
        context = self._build_context()

        prompt = f"""{context}

Perform a comprehensive autonomous analysis of this dataset. Generate exactly 6 key insights.

Return ONLY valid JSON array with this structure:
[
  {{
    "title": "Short insight title",
    "body": "Detailed explanation with specific numbers",
    "type": "info|warning|success|danger",
    "category": "quality|distribution|correlation|outlier|trend|recommendation"
  }}
]

Focus on:
1. Data quality (missing values, duplicates)
2. Distribution characteristics of numeric columns
3. Notable correlations
4. Outliers or anomalies
5. Key patterns in categorical columns
6. Actionable recommendations

Return ONLY the JSON array, no other text."""

        response = self._call_groq(
            [{"role": "user", "content": prompt}],
            max_tokens=3000,
        )

        try:
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return self._local_insights()

    # Local Insights Fallback 
    def _local_insights(self) -> List[Dict[str, str]]:
        """Generate basic insights without AI."""
        df       = self.df
        insights: List[Dict[str, str]] = []

        # 1. Data completeness
        total_missing = int(df.isnull().sum().sum())
        pct_missing   = total_missing / (df.shape[0] * df.shape[1]) * 100
        insights.append({
            "title":    f"Data Completeness: {100 - pct_missing:.1f}%",
            "body":     (
                f"Dataset contains {total_missing:,} missing values across "
                f"{(df.isnull().sum() > 0).sum()} columns "
                f"({pct_missing:.1f}% of all cells)."
            ),
            "type":     "warning" if pct_missing > 5 else "success",
            "category": "quality",
        })

        # 2. Dataset size
        n_num = len(df.select_dtypes(include="number").columns)
        n_cat = len(df.select_dtypes(include="object").columns)
        insights.append({
            "title":    f"Dataset Scale: {df.shape[0]:,} Records",
            "body":     (
                f"{df.shape[0]:,} rows and {df.shape[1]} columns — "
                f"{n_num} numeric, {n_cat} categorical."
            ),
            "type":     "info",
            "category": "distribution",
        })

        # 3. Skewness
        numeric = df.select_dtypes(include="number")
        if not numeric.empty:
            skewed = [col for col in numeric.columns if abs(numeric[col].skew()) > 1]
            if skewed:
                insights.append({
                    "title":    "Skewed Distributions Detected",
                    "body":     (
                        f"Columns with high skewness (>1): {', '.join(skewed[:4])}. "
                        "Consider log transformation for modelling."
                    ),
                    "type":     "warning",
                    "category": "distribution",
                })

        # 4. Duplicates
        dup_count = int(df.duplicated().sum())
        insights.append({
            "title":    f"Duplicate Records: {dup_count:,}",
            "body":     (
                f"Found {dup_count:,} exact duplicate rows "
                f"({dup_count / len(df) * 100:.1f}% of dataset). "
                + ("Consider deduplication before modelling." if dup_count else "Dataset is clean.")
            ),
            "type":     "warning" if dup_count else "success",
            "category": "quality",
        })

        # 5. High correlations
        if len(numeric.columns) >= 2:
            corr_matrix = numeric.corr().abs()
            high_corr = [
                (corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j])
                for i in range(len(corr_matrix.columns))
                for j in range(i + 1, len(corr_matrix.columns))
                if corr_matrix.iloc[i, j] > 0.7
            ]
            if high_corr:
                pairs_str = ", ".join(
                    f"{a}↔{b} ({v:.2f})" for a, b, v in high_corr[:3]
                )
                insights.append({
                    "title":    f"{len(high_corr)} High Correlation(s) Found",
                    "body":     f"Strongly correlated pairs: {pairs_str}. May indicate multicollinearity.",
                    "type":     "info",
                    "category": "correlation",
                })

        # 6. High-cardinality categoricals
        cat_cols  = df.select_dtypes(include="object").columns
        high_card = [col for col in cat_cols if df[col].nunique() > 50]
        if high_card:
            insights.append({
                "title":    "High Cardinality Columns",
                "body":     (
                    f"Columns with >50 unique values: {', '.join(high_card[:3])}. "
                    "May need encoding strategy for ML."
                ),
                "type":     "warning",
                "category": "recommendation",
            })

        # Pad to 6 if needed
        while len(insights) < 6:
            insights.append({
                "title":    "Add Groq API Key for Deeper Insights",
                "body":     (
                    "Connect your Groq API key (gsk_...) to unlock AI-powered analysis, "
                    "natural language Q&A, and intelligent recommendations."
                ),
                "type":     "info",
                "category": "recommendation",
            })

        return insights[:6]

    def generate_sql(self, question: str) -> str:
        """Convert a natural-language question to a SQL query."""
        schema = self.db_manager.get_schema(self.table_name)
        sample = self.db_manager.get_sample_rows(self.table_name, 2)

        prompt = (
            f"Convert this question to SQL for the table `{self.table_name}`.\n\n"
            f"Table schema:\n{schema}\n\n"
            f"Sample data:\n{sample}\n\n"
            f"Question: {question}\n\n"
            "Return ONLY the SQL query — no explanation, no markdown fences."
        )

        response = self._call_groq(
            [{"role": "user", "content": prompt}],
            max_tokens=512,
        )
        # Strip accidental code fences
        sql = re.sub(r"```sql?\n?|```", "", response).strip()
        return sql