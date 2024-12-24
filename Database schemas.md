# Marts

2 таблицы

ExecutorStatistics

| column                | value type        | meaning                                                                    | example                              |
|-----------------------|-------------------|----------------------------------------------------------------------------|--------------------------------------|
| executor_id           | UUID, Primary key | simply an executor id                                                      | 27232c32-e007-4d42-bc51-e03bc7f18601 |
| acceptance_time       | DOUBLE PRECISION  | average amount of seconds from assigning order to acquiring it by executor | 12.34                                |
| accepted_orders_count | INTEGER           | the number of accepted orders by this executor for all time                | 123                                  |

OrderStatisticsSnapshots

| column            | value type             | meaning                                                                   | example             |
|-------------------|------------------------|---------------------------------------------------------------------------|---------------------|
| snapshot_datetime | TIMESTAMP, Primary key | datetime of taking this snapshot                                          | 2024-12-23 10:00:00 |
| active_count      | INTEGER                | the number of orders with status active at the time of taking snapshot    | 10                  |
| cancelled_count   | INTEGER                | the number of orders with status cancelled at the time of taking snapshot | 1                   |
| done_count        | INTEGER                | the number of orders with status done at the time of taking snapshot      | 100                 |
| avg_order_price   | DOUBLE PRECISION       | average order's final coin amount at the time of taking snapshot          | 123.45              |
| bonus_sum         | DOUBLE PRECISION       | bonus sum from all orders at the time of taking snapshot                  | 12.3                |
| total_coins       | DOUBLE PRECISION       | coin amount from all orders at the time of taking snapshot                | 1234.56             |