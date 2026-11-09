import pandas as pd
import psycopg
import pytest

from src.db import create_table, get_db_config, save_to_postgres
from src.sql_runner import run_daily_returns


@pytest.mark.integration
def test_daily_returns_with_real_postgres(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", "financial_data_test")

    create_table()

    config = get_db_config()

    assert config["dbname"].endswith("_test")

    with psycopg.connect(**config) as connection, connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE btc_ohlcv;")

    df = pd.DataFrame(
    {
        "open_time": pd.to_datetime(
            ["2026-01-01", "2026-01-02", "2026-01-03"]
        ),
        "open": [100, 100, 110],
        "high": [105, 115, 112],
        "low": [95, 98, 95],
        "close": [100, 110, 99],
        "volume": [10, 20, 30],
    }
    )

    save_to_postgres(df)
    
    result = run_daily_returns("sql/daily_returns.sql")

    assert len(result) == 3
    assert pd.isna(result.iloc[0]["daily_return"])
    assert float(result.iloc[1]["daily_return"]) == pytest.approx(0.1)
    assert float(result.iloc[2]["daily_return"]) == pytest.approx(-0.1)