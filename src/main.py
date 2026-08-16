import logging

from src.config import BATCH_DAYS, END_DATE, OUTPUT_FILE, START_DATE
from src.extract import fetch_data
from src.load import save_data
from src.logger_config import setup_logging
from src.transform import transform_data
from src.validate import validate_data

logger = logging.getLogger(__name__)


def main() -> None:
    """Uruchamia cały pipeline ETL."""

    setup_logging()

    logger.info("Pipeline started")

    all_data = fetch_data(START_DATE, END_DATE, BATCH_DAYS)

    df = transform_data(all_data)

    validate_data(df)

    save_data(df, OUTPUT_FILE)

    logger.info("Pipeline finished successfully")

if __name__ == "__main__":
    main()

