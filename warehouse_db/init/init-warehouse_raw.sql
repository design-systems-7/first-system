CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS dblink;

CREATE TABLE IF NOT EXISTS raw_orders (
    assigned_order_id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    executer_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    coin_coeff FLOAT NOT NULL,
    coin_bonus_amount FLOAT NOT NULL,
    final_coin_amount FLOAT NOT NULL,
    route_information TEXT NOT NULL,
    assign_time TIMESTAMP NOT NULL,
    acquire_time TIMESTAMP,
    updated_at TIMESTAMP NOT NULL,
    dw_loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_orders_updated_at ON raw_orders(updated_at);
CREATE INDEX IF NOT EXISTS idx_raw_orders_order_id ON raw_orders(order_id);
CREATE INDEX IF NOT EXISTS idx_raw_orders_executer_id ON raw_orders(executer_id);
CREATE INDEX IF NOT EXISTS idx_raw_orders_status ON raw_orders(status);

CREATE TABLE IF NOT EXISTS etl_metadata (
    table_name VARCHAR(100) PRIMARY KEY,
    last_sync_time TIMESTAMP NOT NULL
);

INSERT INTO etl_metadata (table_name, last_sync_time)
VALUES ('raw_orders', '2024-01-01 00:00:00')
ON CONFLICT (table_name) DO NOTHING;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO CURRENT_USER;
