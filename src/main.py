import logging

import logger_config
from config import START_DATE, END_DATE, BATCH_DAYS, OUTPUT_FILE
from extract import fetch_data
from transform import transform_data
from validate import validate_data
from load import save_data

logger = logging.getLogger(__name__)


def main():
    logger.info("Pipeline started")

    all_data = fetch_data(START_DATE, END_DATE, BATCH_DAYS)

    df = transform_data(all_data)

    validate_data(df, START_DATE, END_DATE)

    save_data(df, OUTPUT_FILE)

    logger.info("Pipeline finished successfully")

if __name__ == "__main__":
    main()

