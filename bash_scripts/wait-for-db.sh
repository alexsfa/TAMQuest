#!/bin/sh

set -e

# Wait db service and the database that hosts to be ready
until pg_isready -d "$DATABASE_URL"; do
  echo "Waiting for database to be ready..."
  sleep 2
done

echo "DATABASE IS READY!"

# Wait for migrations from supabase_cli service
until psql "$DATABASE_URL" -c '\dt public.questionnaires' | grep -q questionnaires; do
  echo "Waiting for migrations to complete..."
  sleep 2
done

echo "MIGRATIONS COMPLETED!"

exec "$@"