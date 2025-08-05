#!/bin/bash

set -e

# Wait for the DB to be ready
until pg_isready -d "$DATABASE_URL"; do
  echo "Waiting for database to be ready..."
  sleep 2
done

until psql "$DATABASE_URL" -c "SELECT 1 FROM auth.users LIMIT 1;" > /dev/null 2>&1; do
    echo "Waiting for auth.users table to be ready..."
    sleep 2
done

echo "auth.users table is ready. Running migrations..."

for f in /workspace/migrations/table_inits.sql; do
  echo "Applying migration: $f"
  psql "$DATABASE_URL" -f "$f"
done

echo "Migrations applied. Starting main process..."
