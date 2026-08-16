import logging

import src.logger_config
from src.config import START_DATE, END_DATE, BATCH_DAYS, OUTPUT_FILE
from src.extract import fetch_data
from src.transform import transform_data
from src.validate import validate_data
from src.load import save_data

logger = logging.getLogger(__name__)


def main() -> None:
    """Uruchamia cały pipeline ETL."""

    logger.info("Pipeline started")

    all_data = fetch_data(START_DATE, END_DATE, BATCH_DAYS)

    df = transform_data(all_data)

    validate_data(df)

    save_data(df, OUTPUT_FILE)

    logger.info("Pipeline finished successfully")

if __name__ == "__main__":
    main()

