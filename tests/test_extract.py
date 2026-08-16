from datetime import datetime, timezone

import pytest
import requests

from src.extract import fetch_data


def test_fetch_data_returns_api_data(monkeypatch):

    fake_response = [
        [
            1767225600000,
            "87648.21",
            "88919.45",
            "87550.43",
            "88839.04",
            "6279.57133",
            1767311999999,
            "550000000.00",
            100000,
            "3000.00",
            "260000000.00",
            0
        ]
    ]

    class FakeResponse:

        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return fake_response

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "src.extract.requests.get",
        fake_get
    )

    data = fetch_data(
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 2, tzinfo=timezone.utc),
        1
    )

    assert len(data) == 1
    assert data[0][0] == 1767225600000


def test_fetch_data_handles_api_error(monkeypatch):

    def fake_get(*args, **kwargs):
        raise requests.RequestException("Connection error")

    monkeypatch.setattr(
        "src.extract.requests.get",
        fake_get
    )

    with pytest.raises(RuntimeError):
        fetch_data(
            datetime(2026, 1, 1, tzinfo=timezone.utc),
            datetime(2026, 1, 2, tzinfo=timezone.utc),
            1
        )