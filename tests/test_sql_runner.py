import pandas as pd

from src.sql_runner import run_daily_returns


def test_run_daily_returns(tmp_path):

    csv_path = tmp_path / "test_data.csv"

    df_input = pd.DataFrame({
        "open_time": [
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
        ],
        "close": [
            100.0,
            110.0,
            105.0,
        ],
    })

    df_input.to_csv(csv_path, index=False)

    df = run_daily_returns(
        "sql/daily_returns.sql",
        str(csv_path),
    )

    assert isinstance(df, pd.DataFrame)

    assert list(df.columns) == [
        "open_time",
        "close",
        "previous_close",
        "daily_return",
    ]

    assert len(df) == 3

    assert pd.isna(df.iloc[0]["daily_return"])

    assert df.iloc[1]["daily_return"] == 0.1

    assert df.iloc[2]["daily_return"] < 0