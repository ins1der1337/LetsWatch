#!/usr/bin/env bash

set -e

echo "Run migrations..."
cd ./src
alembic upgrade head
cd ..
echo "Migrations applied!"

exec "$@"