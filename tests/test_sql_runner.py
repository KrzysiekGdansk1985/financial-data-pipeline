import pandas as pd

from src.sql_runner import run_daily_returns


def test_run_daily_returns():

    df = run_daily_returns("sql/daily_returns.sql")

    assert isinstance(df, pd.DataFrame)

    assert list(df.columns) == [
        "open_time",
        "close",
        "previous_close",
        "daily_return"
    ]

    assert len(df) == 10

    assert pd.isna(df.iloc[0]["daily_return"])

    assert df.iloc[1]["daily_return"] > 0