from pathlib import Path

import duckdb
import pandas as pd


def run_daily_returns(sql_path: str) -> pd.DataFrame:
    sql = Path(sql_path).read_text(encoding="utf-8")

    with duckdb.connect() as con:
        return con.execute(sql).fetchdf()