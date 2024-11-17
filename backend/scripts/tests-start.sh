#!/usr/bin/env bash

set -e  # Exit on error
set -x  # Print commands for debugging

echo "Running pre-start checks..."
python app/backend_pre_start.py

echo "Running tests..."
pytest app/tests -v

echo "Running tests with coverage..."
coverage run --source=app -m pytest
coverage report --show-missing


