from pathlib import Path

import pandas as pd
import psycopg

from src.db import get_db_config


def run_daily_returns(sql_path: str) -> pd.DataFrame:
    sql = Path(sql_path).read_text(encoding="utf-8")

    config = get_db_config()

    with psycopg.connect(**config) as connection, connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    columns = [
        "open_time",
        "close",
        "previous_close",
        "daily_return",
]

    df = pd.DataFrame(rows, columns=columns)

    return df
