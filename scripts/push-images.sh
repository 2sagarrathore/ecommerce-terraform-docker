#!/usr/bin/env bash
# Builds the five images for linux/amd64 (+ linux/arm64) and pushes them to
# Docker Hub. Multi-arch matters: a plain `docker build` on an Apple Silicon
# Mac produces arm64-only images, which a t3.micro EC2 instance cannot run.
#
# Usage:
#   docker login
#   DOCKERHUB_USERNAME=youruser ./scripts/push-images.sh
#
# Environment:
#   IMAGE_TAG   image tag to push alongside :latest   (default 1.0.0)
#   PLATFORMS   target platforms                      (default linux/amd64,linux/arm64)
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -z "${DOCKERHUB_USERNAME:-}" ]]; then
  echo "DOCKERHUB_USERNAME must be set." >&2
  exit 1
fi
: "${IMAGE_TAG:=1.0.0}"
: "${PLATFORMS:=linux/amd64,linux/arm64}"

SERVICES=(user-service products-service orders-service cart-service frontend)
BUILDER=shopkart-builder

# A dedicated buildx builder is required for multi-platform builds; the default
# "docker" driver can only build for the host architecture.
if ! docker buildx inspect "$BUILDER" >/dev/null 2>&1; then
  echo "==> Creating buildx builder '$BUILDER'"
  docker buildx create --name "$BUILDER" --driver docker-container --bootstrap >/dev/null
fi
docker buildx use "$BUILDER"

echo "==> Building and pushing for: ${PLATFORMS}"
for svc in "${SERVICES[@]}"; do
  echo
  echo "--- ${DOCKERHUB_USERNAME}/shopkart-${svc} ---"
  docker buildx build \
    --platform "${PLATFORMS}" \
    --tag "${DOCKERHUB_USERNAME}/shopkart-${svc}:${IMAGE_TAG}" \
    --tag "${DOCKERHUB_USERNAME}/shopkart-${svc}:latest" \
    --push \
    "services/${svc}"
done

echo
echo "==> Pushed images"
for svc in "${SERVICES[@]}"; do
  echo "    ${DOCKERHUB_USERNAME}/shopkart-${svc}:${IMAGE_TAG}"
done
echo
echo "Set dockerhub_username = \"${DOCKERHUB_USERNAME}\" in terraform/terraform.tfvars, then run terraform apply."
