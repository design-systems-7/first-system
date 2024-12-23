
CREATE TABLE IF NOT EXISTS ExecutorStatistics (
    executor_id UUID PRIMARY KEY,
    acceptance_time INTERVAL,
    accepted_orders_count INTEGER
);


CREATE TABLE IF NOT EXISTS OrderStatisticsSnapshots (
    snapshot_datetime TIMESTAMP PRIMARY KEY,
    active_count INTEGER NOT NULL DEFAULT 0,
    cancelled_count INTEGER NOT NULL DEFAULT 0,
    done_count INTEGER NOT NULL DEFAULT 0,
    avg_order_price DOUBLE PRECISION,
    bonus_sum DOUBLE PRECISION NOT NULL DEFAULT 0,
    total_coins DOUBLE PRECISION NOT NULL DEFAULT 0
);


CREATE TABLE IF NOT EXISTS OrderStatisticsDeltas (
    snapshot_datetime TIMESTAMP,
    snapshot_datetime_from TIMESTAMP,
    active_count_delta INTEGER NOT NULL DEFAULT 0,
    cancelled_count_delta INTEGER NOT NULL DEFAULT 0,
    done_count_delta INTEGER NOT NULL DEFAULT 0,
    avg_order_price_in_slice DOUBLE PRECISION,
    bonus_sum_in_slice DOUBLE PRECISION NOT NULL DEFAULT 0,
    total_coins_in_slice DOUBLE PRECISION NOT NULL DEFAULT 0,
    PRIMARY KEY (snapshot_datetime, snapshot_datetime_from)
);


CREATE INDEX IF NOT EXISTS idx_order_statistics_deltas_from 
ON OrderStatisticsDeltas(snapshot_datetime_from);