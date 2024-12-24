# design-systems-7-first-system

## Инструкции для тестирования

1. Выполнить `./launch.sh` и дождаться запуска всех контейнеров.
2. Запустить скрипт `assign_and_issue_orders.py` для симуляции реальной работы системы.
3. Чтобы увидеть интерфейс airflow, нужно в браузере перейти на `localhost:8080`.
4. Логин - `airflow`, пароль - `airflow`.
5. Чтобы проверить работоспособность airflow, можно запустить DAG под названием `count_db_entries`.

6. Создать connections (admin/connections)
```
connection id: raw_dwh_layer
type: posgress
host: raw_dwh_layer
database: app
login: postgres
password: changethis
port: 5434
```

```
connection id: postgres_marts
type: posgress
host: postgres-marts
database: marts
login: marts
password: marts
port: 5433
```

7. Включить DAG `update_marts` -- http://127.0.0.1:8080/dags/update_marts/grid?tab=details. 
Он запускается раз в минуту.
8. Дашборды расположены в Графане по адресу `localhost:3000`. 
9. Логин - `admin`, пароль - `admin`.
10. Для начала работы с дашбордами нужно будет добавить data source

```
host url: postgres-marts:5433
database: marts
login: marts
password: marts
ssl mode: disabled
```

11. Импортировать дашборды из `grafana/main_dashboard.json`
