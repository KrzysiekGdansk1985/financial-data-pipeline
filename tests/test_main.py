from src import main


def test_main_pipeline(monkeypatch):

    fake_data = [
        ["fake_record"]
    ]

    def fake_fetch_data(start_date, end_date, batch_days):
        return fake_data

    def fake_transform_data(all_data):
        return "fake_dataframe"

    def fake_validate_data(df):
        return None

    saved_data = {}

    def fake_save_data(df, file_path):
        saved_data["df"] = df
        saved_data["file_path"] = file_path

    monkeypatch.setattr(
        main,
        "fetch_data",
        fake_fetch_data
    )

    monkeypatch.setattr(
        main,
        "transform_data",
        fake_transform_data
    )

    monkeypatch.setattr(
        main,
        "validate_data",
        fake_validate_data
    )

    monkeypatch.setattr(
        main,
        "save_data",
        fake_save_data
    )

    main.main()

    assert saved_data["df"] == "fake_dataframe"
    assert saved_data["file_path"] == main.OUTPUT_FILE