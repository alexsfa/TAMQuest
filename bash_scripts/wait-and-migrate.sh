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

echo "Migrations are successfully applied."

until curl -s http://auth:8081/health > /dev/null; do
  echo "Waiting for auth service to be ready..."
  sleep 2
done

echo "Auth service is ready."

echo "Bootstrapping admin user..."
if python3 /workspace/scripts/init_admin_user.py; then
  echo "Admin bootstrap completed successfully!"
else 
  echo "Failed to create admin user, continuing..."
fi

echo "$SERVICE_ROLE_KEY"

echo "Starting the main process.."

exec "$@"
