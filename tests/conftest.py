import psycopg
import pytest

from src.db import create_table, get_db_config


@pytest.fixture
def postgres_test_db(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", "financial_data_test")

    create_table()

    config = get_db_config()

    assert config["dbname"].endswith("_test")

    with psycopg.connect(**config) as connection, connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE btc_ohlcv;")

    yield

    with psycopg.connect(**config) as connection, connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE btc_ohlcv;")