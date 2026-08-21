WITH prices AS (
    SELECT
        open_time,
        close,
        LAG(close) OVER (ORDER BY open_time) AS previous_close
    FROM 'data/btcusdt_ohlcv.csv'
)
SELECT
    open_time,
    close,
    previous_close,
    (close - previous_close) / previous_close AS daily_return
FROM prices
ORDER BY open_time;