from pathlib import Path

import duckdb
import pandas as pd


def run_daily_returns(
    sql_path: str,
    csv_path: str = "data/btcusdt_ohlcv.csv",
) -> pd.DataFrame:
    sql = Path(sql_path).read_text(encoding="utf-8")

    sql = sql.replace(
        "'data/btcusdt_ohlcv.csv'",
        f"'{csv_path}'",
    )

    with duckdb.connect() as con:
        return con.execute(sql).fetchdf()
