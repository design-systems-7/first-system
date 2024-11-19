#!/usr/bin/env bash

set -x

mypy app
ruff check app
ruff format app --check
