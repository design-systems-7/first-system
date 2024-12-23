
CREATE TABLE IF NOT EXISTS ExecutorStatistics (
    executor_id UUID PRIMARY KEY,
    acceptance_time DOUBLE PRECISION,
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
