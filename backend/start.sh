#!/bin/sh
set -e

# Safety: if DSN points to docker service 'postgres', use container port 5432
if [ -n "$pg_dsn" ]; then
  pg_dsn=$(printf '%s' "$pg_dsn" | sed 's/@postgres:55432\//@postgres:5432\//')
  export pg_dsn
fi

attempt=1
max_attempts=30
until python -m app.utils.ensure_postgres_db && python -m app.utils.seed_admin; do
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "seed bootstrap failed after $attempt attempts"
    exit 1
  fi

  echo "seed bootstrap failed, waiting for postgres... ($attempt/$max_attempts)"
  attempt=$((attempt + 1))
  sleep 2
done

exec uvicorn app.main:app --host 0.0.0.0 --port 1111