#!/usr/bin/env bash
# Builds all five images, starts them locally and verifies every endpoint.
# Usage: DOCKERHUB_USERNAME=youruser ./scripts/build-and-test.sh
set -euo pipefail

cd "$(dirname "$0")/.."

: "${DOCKERHUB_USERNAME:=local}"
: "${IMAGE_TAG:=1.0.0}"
: "${FRONTEND_HOST_PORT:=8080}"
export DOCKERHUB_USERNAME IMAGE_TAG FRONTEND_HOST_PORT

echo "==> Building images as ${DOCKERHUB_USERNAME}/shopkart-*:${IMAGE_TAG}"
docker compose build

echo "==> Starting the stack"
docker compose up -d

echo "==> Waiting for the frontend to become healthy"
for _ in $(seq 1 40); do
  if curl -fsS --max-time 2 "http://localhost:${FRONTEND_HOST_PORT}/health" >/dev/null 2>&1; then break; fi
  sleep 2
done

fail=0
check() {
  local label="$1" url="$2" expect="$3"
  local body
  if body="$(curl -fsS --max-time 5 "$url" 2>/dev/null)" && grep -q "$expect" <<<"$body"; then
    printf 'OK      %-18s %s\n' "$label" "$url"
  else
    printf 'FAILED  %-18s %s\n' "$label" "$url"
    fail=1
  fi
}

echo
echo "==> Endpoint checks"
check "user-service"     "http://localhost:3001/"       "user Service Running"
check "products-service" "http://localhost:3002/"       "products Service Running"
check "orders-service"   "http://localhost:3003/"       "orders Service Running"
check "cart-service"     "http://localhost:3004/"       "cart Service Running"
check "frontend page"    "http://localhost:${FRONTEND_HOST_PORT}/" "Frontend is Live"
check "aggregated state" "http://localhost:${FRONTEND_HOST_PORT}/api/status" '"healthy":4'

echo
docker compose ps
exit "$fail"
