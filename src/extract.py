import logging
import requests
from datetime import datetime, timedelta

from src.config import SYMBOL, INTERVAL

logger = logging.getLogger(__name__)

url = "https://api.binance.com/api/v3/klines"

def fetch_data(start_date: datetime, end_date: datetime, batch_days: int) -> list:

    all_data = []
    current_date = start_date

    while current_date < end_date:

        next_date = min(
            current_date + timedelta(days=batch_days),
            end_date
        )

        logger.info("Batch: %s → %s", current_date, next_date)

        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "startTime": int(current_date.timestamp() * 1000),
            "endTime": int(next_date.timestamp() * 1000),
            "limit": 1000
        }

        try:
            response = requests.get(url, params=params, timeout=10)

        except requests.RequestException as e:
            logger.error("API request failed: %s", e)
            raise RuntimeError(f"API request failed: {e}")

        logger.info("Status: %s", response.status_code)

        response.raise_for_status()

        data = response.json()

        logger.info("Records: %s", len(data))

        all_data.extend(data)

        current_date = next_date + timedelta(days=1)

    return all_data