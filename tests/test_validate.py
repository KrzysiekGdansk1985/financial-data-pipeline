import pandas as pd
import pytest

from src.validate import validate_data


def test_validate_data_detects_missing_values():

    df = pd.DataFrame({
        "open_time": pd.to_datetime([
            "2026-01-01",
            "2026-01-02"
        ]),
        "open": [100.0, None],
        "high": [110.0, 120.0],
        "low": [90.0, 95.0],
        "close": [105.0, 115.0],
        "volume": [1000.0, 1200.0]
    })

    with pytest.raises(ValueError):
        validate_data(df)

def test_validate_data_detects_duplicates():

    df = pd.DataFrame({
        "open_time": pd.to_datetime([
            "2026-01-01",
            "2026-01-01"
        ]),
        "open": [100.0, 100.0],
        "high": [110.0, 110.0],
        "low": [90.0, 90.0],
        "close": [105.0, 105.0],
        "volume": [1000.0, 1000.0]
    })

    with pytest.raises(ValueError):
        validate_data(df)

def test_validate_data_accepts_valid_data():

    df = pd.DataFrame({
        "open_time": pd.to_datetime([
            "2026-01-01",
            "2026-01-02"
        ]),
        "open": [100.0, 110.0],
        "high": [110.0, 120.0],
        "low": [90.0, 100.0],
        "close": [105.0, 115.0],
        "volume": [1000.0, 1200.0]
    })

    validate_data(df)