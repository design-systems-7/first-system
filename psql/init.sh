#!/bin/bash

DB_NAME="marts"
DB_USER="marts"
DB_HOST="localhost"
DB_PORT="5432"
SQL_FILE="create_marts_tables.sql"

psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -f $SQL_FILE