# Financial Data Pipeline

ETL pipeline for collecting and processing BTCUSDT OHLCV data from the Binance API.

## Project Overview

The project downloads historical BTCUSDT daily market data from the Binance API, transforms the raw data using Pandas, validates data quality, and saves the processed dataset to a CSV file.

The pipeline follows the ETL pattern:

Extract → Transform → Validate → Load

## Technologies

- Python
- Pandas
- Requests
- Binance API
- Git

## Project Structure
```text
financial-data-pipeline/
│
├── data/
│   └── btcusdt_ohlcv.csv
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   └── logger_config.py
│
├── .gitignore
├── requirements.txt
└── README.md
```
## Pipeline

1. Extract

Data is downloaded from the Binance API using the requests library.
The pipeline supports downloading data in batches to avoid requesting the entire time range in a single API request.

2. Transform

Raw API data is converted into a Pandas DataFrame.
The transformation includes:
- converting timestamps to datetime,
- converting OHLCV columns to numeric types,
 - creating a structured tabular dataset.

3. Validate

The pipeline performs basic data-quality checks:
- empty dataset,
- missing values,
- duplicate rows,
- timestamp ordering,
- OHLC consistency.

4. Load

The processed dataset is saved as:
data/btcusdt_ohlcv.csv

## Configuration

1. Pipeline parameters are stored in:
src/config.py
2. Current configuration includes:
- trading symbol,
- interval,
- start date,
- end date,
- batch size,
- output file.

## Logging

1. Pipeline execution is logged to:
pipeline.log
2. The log contains information about:
- pipeline execution,
- API requests,
- number of downloaded records,
- data validation,
- output file creation.

## Installation

1. Create a virtual environment:
- python -m venv .venv
2. Activate the environment:
- .venv\Scripts\Activate.ps1
3. Install dependencies:
- python -m pip install -r requirements.txt

## Running the Pipeline

1. Run:
- python src/main.py
2. After successful execution, the processed data is saved to:
- data/btcusdt_ohlcv.csv


