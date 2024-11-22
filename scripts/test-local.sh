#!/usr/bin/env bash

set -e  # Exit on error
set -x  # Print commands for debugging

# Cleanup
docker-compose down -v --remove-orphans

if [ $(uname -s) = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

# Build and start services
docker-compose build
docker-compose up prestart -d
sleep 5
docker-compose up backend -d

# Run tests with proper output capturing and timeout
docker-compose exec -T backend bash -c "
    set -e
    chmod +x scripts/tests-start.sh
    timeout 120 scripts/tests-start.sh
"

# Store the exit code
exit_code=$?

# Output logs if tests failed
if [ $exit_code -ne 0 ]; then
    echo "Tests failed. Outputting service logs..."
    docker-compose logs
fi

# Cleanup after tests
docker-compose down -v --remove-orphans

exit $exit_code
