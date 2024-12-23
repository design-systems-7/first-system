#!/bin/bash

cd airflow

mkdir -p ./dags ./logs ./plugins ./config

cd ..

AIRFLOW_PROJ_DIR=./airflow docker compose -f docker-compose.yml -f airflow/docker-compose.yaml up