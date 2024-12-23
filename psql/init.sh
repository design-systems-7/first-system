#!/bin/bash

DB_NAME="marts"
DB_USER="marts"
DB_HOST="postgres-marts"
DB_PORT="5433"
SQL_FILE="init_marts.sql"

psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -f $SQL_FILE