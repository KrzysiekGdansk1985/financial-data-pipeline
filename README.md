# Financial Data Pipeline

[![CI](https://github.com/KrzysiekGdansk1985/financial-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/KrzysiekGdansk1985/financial-data-pipeline/actions/workflows/ci.yml)

ETL pipeline for collecting, transforming, validating, and analyzing BTCUSDT OHLCV data from the Binance API.

The project demonstrates a complete data engineering workflow including Python-based ETL, data validation, SQL analytics with DuckDB, automated testing, Docker containerization, and CI/CD with GitHub Actions.

---

## Project Overview

The pipeline downloads historical BTCUSDT daily market data from the Binance API and processes it through several stages:

```text
Binance API
     │
     ▼
  Extract
     │
     ▼
 Transform
     │
     ▼
  Validate
     │
     ▼
    Load
     │
     ▼
CSV dataset
     │
     ▼
DuckDB / SQL
     │
     ▼
Daily returns
```

The project also uses GitHub Actions to automatically test the application and build and publish the Docker image.

---

## Technologies

* Python 3.13
* Pandas
* Requests
* DuckDB
* SQL
* Pytest
* Ruff
* Docker
* GitHub Actions
* Docker Hub
* Binance API

---

## Project Structure

```text
financial-data-pipeline/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data/
│   └── btcusdt_ohlcv.csv
│
├── sql/
│   └── daily_returns.sql
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   ├── sql_runner.py
│   └── logger_config.py
│
├── tests/
│   ├── test_extract.py
│   ├── test_load.py
│   ├── test_main.py
│   ├── test_sql_runner.py
│   ├── test_transform.py
│   └── test_validate.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Pipeline

### 1. Extract

Historical BTCUSDT OHLCV data is downloaded from the Binance API using the `requests` library.

The pipeline supports downloading data in batches to avoid requesting the entire time range in a single API request.

### 2. Transform

Raw API data is converted into a Pandas DataFrame.

The transformation includes:

* converting timestamps to datetime,
* converting OHLCV columns to numeric types,
* creating a structured tabular dataset.

### 3. Validate

The pipeline performs basic data-quality checks:

* empty dataset,
* missing values,
* duplicate rows,
* timestamp ordering,
* OHLC consistency.

If validation fails, the pipeline stops and the data is not loaded.

### 4. Load

The validated dataset is saved as:

```text
data/btcusdt_ohlcv.csv
```

### 5. SQL Analytics

The saved CSV file is queried using DuckDB and SQL.

The current SQL transformation calculates daily returns using the previous closing price:

```text
daily_return =
(close - previous_close) / previous_close
```

The SQL query is stored in:

```text
sql/daily_returns.sql
```

---

## Configuration

Pipeline parameters are stored in:

```text
src/config.py
```

The configuration includes:

* trading symbol,
* interval,
* start date,
* end date,
* batch size,
* output file.

---

## Logging

Pipeline execution is logged using Python's `logging` module.

The log contains information about:

* pipeline execution,
* API requests,
* downloaded records,
* data validation,
* output file creation,
* SQL analytics.

Example:

```text
Pipeline started
Status: 200
Records: 10
Missing values: 0
Duplicate rows: 0
OHLC validation: True
Daily returns calculated
Pipeline finished successfully
```

---

## Testing

The project uses `pytest` for automated testing.

Run tests locally with:

```powershell
python -m pytest
```

The test suite covers:

* API data extraction,
* data transformation,
* data validation,
* CSV loading,
* SQL analytics,
* pipeline execution.

Code quality is checked with Ruff:

```powershell
ruff check src tests
```

---

## Docker

The application can be packaged as a Docker image.

### Build the image locally

```powershell
docker build -t financial-data-pipeline:latest .
```

### Run the container

```powershell
docker run --rm -v "${PWD}\data:/app/data" financial-data-pipeline:latest
```

The bind mount makes the local `data` directory available inside the container as:

```text
/app/data
```

---

## Docker Hub

A ready-to-use Docker image is published to Docker Hub:

```text
krzysiekgdansk1985/financial-data-pipeline:latest
```

Pull the image:

```powershell
docker pull krzysiekgdansk1985/financial-data-pipeline:latest
```

Run it:

```powershell
docker run --rm -v "${PWD}\data:/app/data" krzysiekgdansk1985/financial-data-pipeline:latest
```

This allows the pipeline to be executed without building the Docker image locally.

---

## CI/CD

The project uses GitHub Actions for continuous integration and delivery.

The workflow is defined in:

```text
.github/workflows/ci.yml
```

Every push to the `master` branch triggers the following process:

```text
git push
    │
    ▼
GitHub Actions
    │
    ▼
Ruff
    │
    ▼
pytest
    │
    ▼
Docker build
    │
    ▼
Docker Hub
```

The Docker image is built and published only if the tests pass.

The workflow creates two Docker image tags:

```text
latest
```

and:

```text
<Git commit SHA>
```

The commit SHA tag identifies the exact source commit used to build the image.

---

## Running the Pipeline Locally

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate the environment

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Run the pipeline

```powershell
python -m src.main
```

After successful execution, the processed dataset is saved to:

```text
data/btcusdt_ohlcv.csv
```

---

## Running the Pipeline with Docker

Alternatively, the pipeline can be run using the published Docker image:

```powershell
docker pull krzysiekgdansk1985/financial-data-pipeline:latest
```

Then:

```powershell
docker run --rm -v "${PWD}\data:/app/data" krzysiekgdansk1985/financial-data-pipeline:latest
```

No local Python environment is required for the Docker-based execution.

---

## CI/CD Summary

The project demonstrates the following workflow:

```text
Python ETL
    │
    ├── Extract
    ├── Transform
    ├── Validate
    ├── Load
    └── SQL Analytics
          │
          ▼
       Pytest
          │
          ▼
       GitHub Actions
          │
          ▼
      Docker Build
          │
          ▼
       Docker Hub
```

The goal of the project is to demonstrate practical data engineering skills including ETL development, data quality validation, SQL analytics, automated testing, containerization, and CI/CD automation.
