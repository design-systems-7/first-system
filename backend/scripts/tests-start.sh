#! /usr/bin/env bash

coverage run --source=app -m pytest
#coverage report --show-missing
#coverage html --title "${@-coverage}"