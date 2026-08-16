import logging
import pandas as pd

logger = logging.getLogger(__name__)


def save_data(df: pd.DataFrame, file_path: str) -> None:
    df.to_csv(file_path, index=False)
    logger.info("Data saved to: %s", file_path)