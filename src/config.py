from datetime import datetime, timezone


SYMBOL = "BTCUSDT"
INTERVAL = "1d"

START_DATE = datetime(
    2026, 1, 1,
    tzinfo=timezone.utc
)

END_DATE = datetime(
    2026, 1, 10,
    tzinfo=timezone.utc
)

BATCH_DAYS = 5

OUTPUT_FILE = "data/btcusdt_ohlcv.csv"