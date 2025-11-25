#!/bin/bash

set -e

# Wait for the DB to be ready
until pg_isready -d "$DATABASE_URL"; do
  echo "Waiting for database to be ready..."
  sleep 2
done

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

for f in /workspace/migrations/rls_policies.sql; do
  echo "Applying RLS policies: $f"
  psql "$DATABASE_URL" -f "$f"
done
echo "RLS policies are successfully applied."

echo "Bootstrapping admin user..."
if python3 /workspace/scripts/init_admin_user.py; then
  echo "Admin bootstrap completed successfully!"
else 
  echo "Failed to create admin user, continuing..."
fi

echo "Starting the main process.."

exec "$@"
