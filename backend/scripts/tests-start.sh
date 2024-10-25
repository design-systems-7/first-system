#! /usr/bin/env bash
set -e
set -x

python app/backend_pre_start.py

#coverage run --source=app -m pytest
#coverage report --show-missing
#coverage html --title "${@-coverage}"