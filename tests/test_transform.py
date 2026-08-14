import pandas as pd

from src.transform import transform_data


def test_transform_data_converts_types():

    all_data = [[
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
    ]]

    df = transform_data(all_data)

    assert pd.api.types.is_datetime64_dtype(
        df["open_time"]
    )

    assert pd.api.types.is_float_dtype(
        df["open"]
    )

    assert pd.api.types.is_float_dtype(
        df["high"]
    )

    assert pd.api.types.is_float_dtype(
        df["low"]
    )

    assert pd.api.types.is_float_dtype(
        df["close"]
    )

    assert pd.api.types.is_float_dtype(
        df["volume"]
    )