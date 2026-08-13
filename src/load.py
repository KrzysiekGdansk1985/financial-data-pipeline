import logging

logger = logging.getLogger(__name__)


def save_data(df, file_path):
    df.to_csv(file_path, index=False)
    logger.info("Data saved to: %s", file_path)