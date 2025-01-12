#!/bin/bash

# Script to initialize and start the Django application.

# Print waiting message and connection details.
echo "Waiting for postgres..."
echo "Host: $POSTGRES_HOST"
echo "Port: $POSTGRES_PORT"

# Wait for PostgreSQL to be ready by checking connection.
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.1
done

# Notify that PostgreSQL is available.
echo "PostgreSQL started"

# Wait for Redis to be ready by checking connection.
echo "Waiting for redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done

# Notify that Redis is available.
echo "Redis started"

# Execute the main command passed to the container.
exec "$@"
