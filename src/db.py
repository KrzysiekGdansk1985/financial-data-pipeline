import os

import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()


env_to_param = {
    "POSTGRES_HOST": "host",
    "POSTGRES_PORT": "port",
    "POSTGRES_DB": "dbname",
    "POSTGRES_USER": "user",
    "POSTGRES_PASSWORD": "password",
}


def get_db_config() -> dict[str, str]:
    config = {}

    for env_name, param_name in env_to_param.items():
        value = os.getenv(env_name)

        if not value:
            raise ValueError(f"Missing environment variable: {env_name}")

        config[param_name] = value

    return config


def create_table() -> None:
    with open("sql/create_btc_ohlcv.sql", "r", encoding="utf-8") as file:
        sql = file.read()

    config = get_db_config()

    with psycopg.connect(**config) as connection, connection.cursor() as cursor:
        cursor.execute(sql)


def save_to_postgres(df: pd.DataFrame) -> None:
    """
    Save OHLCV data from a pandas DataFrame into PostgreSQL.
    """
    if df.empty:
        return

    rows = [
        (
            row["open_time"],
            row["open"],
            row["high"],
            row["low"],
            row["close"],
            row["volume"],
        )
        for _, row in df.iterrows()
    ]

    upsert_sql = """
        INSERT INTO btc_ohlcv (
            open_time, open, high, low, close, volume
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (open_time)
        DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume;
    """

    config = get_db_config()

    with psycopg.connect(**config) as connection, connection.cursor() as cursor:
        cursor.executemany(upsert_sql, rows)


def read_from_postgres(limit: int = 10) -> pd.DataFrame:
    config = get_db_config()

    sql = """
        SELECT
            open_time,
            open,
            high,
            low,
            close,
            volume
        FROM btc_ohlcv
        ORDER BY open_time DESC
        LIMIT %s;
    """

    with psycopg.connect(**config) as connection, connection.cursor() as cursor:
        cursor.execute(sql, (limit,))
        rows = cursor.fetchall()

    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    df = pd.DataFrame(rows, columns=columns)

    return df