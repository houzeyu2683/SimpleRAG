#!/bin/sh
set -e

echo "Waiting for Redis..."
until redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ping | grep -q PONG; do
    sleep 1
done
echo "Redis is ready."

exec celery -A app.tasks.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    -Q ingest \
    "$@"
