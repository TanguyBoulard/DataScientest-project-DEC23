#!/bin/bash

# Function to check the status of a service
check_service_status() {
    local service=$1
    local status
    local health
    local exit_code

    status=$(docker-compose ps -q $service | xargs docker inspect -f '{{.State.Status}}' 2>/dev/null)
    health=$(docker-compose ps -q $service | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null)
    exit_code=$(docker-compose ps -q $service | xargs docker inspect -f '{{.State.ExitCode}}' 2>/dev/null)

    if [ "$status" = "running" ] && [ "$health" = "healthy" ]; then
        echo "$service is healthy"
        return 0
    elif [ "$status" = "exited" ] && [ "$exit_code" = "0" ]; then
        echo "$service exited with code 0"
        return 0
    else
        echo "$service is not healthy or did not exit with code 0 (Status: $status, Health: $health, Exit Code: $exit_code)"
        return 1
    fi
}

# Function to wait for a service to be healthy or exit with code 0
wait_for_service() {
    local service=$1
    local max_attempts=${2:-60}
    local sleep_time=${3:-10}

    for i in $(seq 1 $max_attempts); do
        if check_service_status $service; then
            return 0
        fi
        echo "Waiting for $service (attempt $i/$max_attempts)"
        sleep $sleep_time
    done

    echo "$service failed to become healthy or exit with code 0"
    docker-compose logs $service
    return 1
}

# Function to check all services
check_all_services() {
    local services=$(docker-compose config --services)
    local failed_services=()

    for service in $services; do
        if ! wait_for_service $service; then
            failed_services+=($service)
        fi
    done

    if [ ${#failed_services[@]} -eq 0 ]; then
        echo "All services are healthy or completed successfully"
        return 0
    else
        echo "The following services failed to become healthy or complete successfully:"
        printf '%s\n' "${failed_services[@]}"
        return 1
    fi
}

# Main execution
check_all_services