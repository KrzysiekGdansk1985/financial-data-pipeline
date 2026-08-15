import pandas as pd

from src.load import save_data


def test_save_data_creates_csv_file(tmp_path):

    df = pd.DataFrame({
        "open_time": ["2026-01-01", "2026-01-02"],
        "open": [100.0, 110.0],
        "close": [105.0, 115.0]
    })

    file_path = tmp_path / "test_data.csv"

    save_data(df, file_path)

    assert file_path.exists()

    saved_df = pd.read_csv(file_path)

    assert len(saved_df) == 2
    assert list(saved_df.columns) == [
        "open_time",
        "open",
        "close"
    ]