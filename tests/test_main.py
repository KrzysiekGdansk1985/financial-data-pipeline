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
    
    def fake_create_table():
        pass
    
    def fake_run_daily_returns(sql_path):
        return "fake_daily_returns"

    saved_data = {}

    def fake_save_to_postgres(df):
        saved_data["df"] = df

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
        "create_table",
        fake_create_table,
    )

    monkeypatch.setattr(
        main,
        "run_daily_returns",
        fake_run_daily_returns
    )
    
    monkeypatch.setattr(
        main,
        "save_to_postgres",
        fake_save_to_postgres
    )


    main.main()

    assert saved_data["df"] == "fake_dataframe"