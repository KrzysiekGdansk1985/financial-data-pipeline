import logging
import pandas as pd

logger = logging.getLogger(__name__)

def validate_data(df: pd.DataFrame) -> None:
    """Sprawdza jakość danych i zgłasza błędy w przypadku nieprawidłowości."""

    if len(df) == 0:
        raise ValueError("Data validation failed: dataset is empty.")

    first_date = df["open_time"].min()
    last_date = df["open_time"].max()

    logger.info("First date: %s", first_date)
    logger.info("Last date: %s", last_date)

    logger.info("Record count: %s", len(df))

    if len(df) < 5:
        logger.warning("Low record count: %s records found.", len(df)
    )

    missing_values = df.isna().sum().sum()

    if missing_values > 0:
        raise ValueError(
            f"Data validation failed: {missing_values} missing values found."
        )

    logger.info("Missing values: 0")

    duplicate_rows = df.duplicated().sum()

    if duplicate_rows > 0:
        raise ValueError(
            f"Data validation failed: {duplicate_rows} duplicate rows found."
        )

    logger.info("Duplicate rows: 0")

    if not df["open_time"].is_monotonic_increasing:
        raise ValueError(
            "Data validation failed: timestamps are not sorted."
        )

    logger.info("Data sorted: True")

    invalid_ohlc = ((df["high"] < df["open"]) | (df["high"] < df["close"]) |
    (df["low"] > df["open"]) | (df["low"] > df["close"])).sum()

    if invalid_ohlc > 0:
        raise ValueError(f"Data validation failed: {invalid_ohlc} invalid OHLC rows found."    )

    logger.info("OHLC validation: True")