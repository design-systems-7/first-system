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
docker-compose up -d

# Function to check if a service is healthy
check_service() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep $service | grep -q "Up"; then
            if [ "$service" = "backend" ]; then
                # Additional health check for backend
                if curl -f http://localhost:8000/api/v1/utils/health-check/ 2>/dev/null; then
                    echo "$service is ready"
                    return 0
                fi
            else
                echo "$service is ready"
                return 0
            fi
        fi
        echo "Attempt $attempt/$max_attempts: $service is not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "$service failed to become ready"
    return 1
}

# Wait for all required services
check_service "db" || exit 1
check_service "redis_cache" || exit 1
check_service "external_apis" || exit 1
check_service "backend" || exit 1

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