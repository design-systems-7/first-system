# Primary db and raw layer

One table

Order

| column            | value type        | meaning                                                                                | example                              |
|-------------------|-------------------|----------------------------------------------------------------------------------------|--------------------------------------|
| assigned_order_id | UUID, Primary key | unique id of the order, assigned by system itself                                      | b01d2fc8-5699-4116-8f53-93a03adb16e3 |
| order_id          | UUID              | id of the order from external service, can be duplicated                               | 1c60f29e-7624-4e70-aaa2-7909c461ddf2 |
| executer_id       | UUID              | executor id                                                                            | 27232c32-e007-4d42-bc51-e03bc7f18601 |
| status            | STRING            | status of the order, one of the values "active", "cancelled", "done"                   | active                               |
| route_information | STRING            | information about zone, depending on executor rating can be "No information available" |                                      |
| coin_coeff        | DOUBLE PRECISION  | order's 'price' coefficient, calculated from route_information                         | 1.3                                  |
| coin_bonus_amount | DOUBLE PRECISION  | bonus coins to the order 'price'                                                       | 12.3                                 |
| final_coin_amount | DOUBLE PRECISION  | final order 'price'                                                                    | 123.56                               |
| assign_time       | TIMESTAMP         | datetime of order's assigning                                                          | 2024-12-23 17:00:24                  |
| acquire_time      | TIMESTAMP         | datetime of order's acquiring by executor                                              | 2024-12-23 17:02:30                  |
| updated_at        | TIMESTAMP         | datetime of order's last update                                                        | 2024-12-23 17:02:30                  |


# Marts

Two tables

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