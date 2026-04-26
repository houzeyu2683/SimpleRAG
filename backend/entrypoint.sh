#!/bin/sh
set -e

echo "Waiting for MariaDB..."
until python -c "
import asyncio, aiomysql, os
async def check():
    await aiomysql.connect(
        host=os.getenv('MARIADB_HOST', 'mariadb'),
        port=int(os.getenv('MARIADB_PORT', 3306)),
        user=os.getenv('MARIADB_USER'),
        password=os.getenv('MARIADB_PASSWORD'),
        db=os.getenv('MARIADB_DATABASE'),
    )
asyncio.run(check())
" 2>/dev/null; do
    sleep 2
done
echo "MariaDB is ready."

echo "Running migrations..."
alembic upgrade head

if [ "${SKIP_SEED:-0}" = "0" ]; then
    echo "Seeding database..."
    python -m app.db.init_db
fi

echo "Starting server..."
exec "$@"
