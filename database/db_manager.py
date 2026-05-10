import pandas as pd
import sqlite3
import os
import streamlit as st
from typing import Optional, Tuple


class DatabaseManager:
    """
    Manages data persistence using SQLite (default) or MySQL.
    Provides SQL query execution and schema inspection.
    """

    def __init__(self, use_mysql: bool = False, mysql_config: dict = None):
        self.use_mysql = use_mysql
        self.mysql_config = mysql_config or {}
        self.db_path = "datamind_agent.db"
        self._tables = {}

        if use_mysql:
            self._init_mysql()
        else:
            self._init_sqlite()

    def _init_sqlite(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def _init_mysql(self):
        try:
            import mysql.connector
            self.conn = mysql.connector.connect(
                host=self.mysql_config.get("host", "localhost"),
                port=self.mysql_config.get("port", 3306),
                user=self.mysql_config.get("user", "root"),
                password=self.mysql_config.get("password", "helloworld@123"),
                database=self.mysql_config.get("database", "datamind"),
            )
        except Exception as e:
            st.warning(f"MySQL connection failed, falling back to SQLite: {e}")
            self.use_mysql = False
            self._init_sqlite()

    # Store DataFrame 
    def store_dataframe(self, df: pd.DataFrame, table_name: str) -> bool:
        """Store a pandas DataFrame as a SQL table."""
        try:
            clean_name = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)
            df.to_sql(clean_name, self.conn, if_exists="replace", index=False)
            self._tables[clean_name] = df.dtypes.to_dict()
            return True
        except Exception as e:
            st.error(f"DB store error: {e}")
            return False

    # Execute Query 
    def execute_query(self, sql: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Execute a SQL query and return (DataFrame, error_message)."""
        try:
            result_df = pd.read_sql_query(sql, self.conn)
            return result_df, None
        except Exception as e:
            return None, str(e)

    # Schema Info 
    def get_schema(self, table_name: str) -> str:
        """Return schema description for AI context."""
        try:
            if self.use_mysql:
                result, err = self.execute_query(f"DESCRIBE `{table_name}`")
            else:
                result, err = self.execute_query(
                    f"PRAGMA table_info({table_name})"
                )
            if err:
                return f"Schema unavailable: {err}"
            return result.to_string(index=False) if result is not None else ""
        except Exception as e:
            return str(e)

    def get_table_names(self) -> list:
        """List all tables in the database."""
        try:
            if self.use_mysql:
                result, _ = self.execute_query("SHOW TABLES")
            else:
                result, _ = self.execute_query(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            if result is not None:
                return result.iloc[:, 0].tolist()
            return []
        except Exception:
            return []

    def get_sample_rows(self, table_name: str, n: int = 3) -> str:
        """Return sample rows as string for AI context."""
        result, err = self.execute_query(f"SELECT * FROM {table_name} LIMIT {n}")
        if result is not None:
            return result.to_string(index=False)
        return ""

    def close(self):
        if self.conn:
            self.conn.close()