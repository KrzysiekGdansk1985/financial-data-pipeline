import logging
from datetime import datetime, timezone

#import logger_config
from extract import fetch_data
from transform import transform_data
from validate import validate_data
from load import save_data

logger = logging.getLogger(__name__)


def main():
    logger.info("Pipeline started")

    start_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2026, 1, 10, tzinfo=timezone.utc)
    batch_days = 5

    all_data = fetch_data(start_date, end_date, batch_days)

    df = transform_data(all_data)

    validate_data(df, start_date, end_date)

    save_data(df, "data/btcusdt_ohlcv.csv")

    logger.info("Pipeline finished successfully")

if __name__ == "__main__":
    main()

