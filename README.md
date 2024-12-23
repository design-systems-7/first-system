# design-systems-7-first-system

## Инструкции для тестирования

1. Выполнить `./launch.sh` и дождаться запуска всех контейнеров.
2. Чтобы увидеть интерфейс airflow, нужно в браузере перейти на `localhost:8080`.
3. Логин - `airflow`, пароль - `airflow`.
4. Чтобы проверить работоспособность airflow, можно запустить DAG под названием `count_db_entries`.



5. Создайте connections (admin/connections)
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

6. Включить DAG `update_marts` -- http://127.0.0.1:8080/dags/update_marts/grid?tab=details



