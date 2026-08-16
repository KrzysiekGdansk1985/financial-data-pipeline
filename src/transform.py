import pandas as pd

def transform_data(all_data: list) -> pd.DataFrame:
    """Przekształca surowe dane OHLCV do DataFrame i konwertuje typy danych."""

    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore"
    ]

    df = pd.DataFrame(all_data, columns=columns)

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    df[numeric_columns] = df[numeric_columns].astype(float)
    
    return df