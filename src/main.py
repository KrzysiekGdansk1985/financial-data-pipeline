import requests
from datetime import datetime, timezone, timedelta
import pandas as pd

url = "https://api.binance.com/api/v3/klines"


def fetch_data(start_date, end_date, batch_days):

    all_data = []
    current_date = start_date

    while current_date < end_date:

        next_date = min(
            current_date + timedelta(days=batch_days),
            end_date
        )

        print("Batch:", current_date, "→", next_date)

        params = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "startTime": int(current_date.timestamp() * 1000),
            "endTime": int(next_date.timestamp() * 1000),
            "limit": 1000
        }

        response = requests.get(url, params=params)

        print("Status:", response.status_code)

        response.raise_for_status()

        data = response.json()

        print("Records:", len(data))

        all_data.extend(data)

        current_date = next_date + timedelta(days=1)

    return all_data


def transform_data(all_data):

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


def save_data(df, file_path):
    df.to_csv(file_path, index=False)


def main():
    start_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2026, 1, 10, tzinfo=timezone.utc)
    batch_days = 5

    all_data = fetch_data(start_date, end_date, batch_days)

    print("Total records:", len(all_data))

    df = transform_data(all_data)

    save_data(df, "data/btcusdt_ohlcv.csv")

if __name__ == "__main__":
    main()

