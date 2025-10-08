#!/bin/sh
set -e

HOST="${GOTRUE_HOST:-auth}"
PORT="${GOTRUE_PORT:-8081}"
SLEEP_TIME=2

echo "Waiting for GoTrue at $HOST:$PORT"

while ! curl -sf "http://$HOST:$PORT/.well-known/jwks.json" > /dev/null; do
    echo "GoTrue not ready yet at $HOST:$PORT, retrying in ${SLEEP_TIME}s..."
    sleep "$SLEEP_TIME"
done

echo "✅ GoTrue is up and responding at $HOST:$PORT"