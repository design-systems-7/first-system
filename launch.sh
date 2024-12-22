#!/bin/bash

docker network create first-system_default 2>/dev/null || true

cd airflow

mkdir -p ./dags ./logs ./plugins ./config

docker compose up airflow-init

cd ..

AIRFLOW_PROJ_DIR=./airflow docker compose -f docker-compose.yml -f airflow/docker-compose.yaml up