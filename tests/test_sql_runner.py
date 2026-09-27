import pandas as pd

from src import sql_runner
from src.sql_runner import run_daily_returns


def test_run_daily_returns(monkeypatch):

    fake_rows = [
        ("2026-01-01", 100.0, None, None),
        ("2026-01-02", 110.0, 100.0, 0.1),
        ("2026-01-03", 105.0, 110.0, -0.04545),
    ]

    class FakeCursor:
        def execute(self, sql):
            pass

        def fetchall(self):
            return fake_rows

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def fake_connect(**kwargs):
        return FakeConnection()

    def fake_get_db_config():
        return {
            "host": "fake_host",
            "port": "1234",
            "dbname": "fake_db",
            "user": "fake_user",
            "password": "fake_password",
        }

    monkeypatch.setattr(
        sql_runner.psycopg,
        "connect",
        fake_connect,
    )

    monkeypatch.setattr(
        sql_runner,
        "get_db_config",
        fake_get_db_config,
    )

    df = run_daily_returns("sql/daily_returns.sql")

    assert len(df) == 3
    assert df.iloc[1]["daily_return"] == 0.1
    assert pd.isna(df.iloc[0]["previous_close"])