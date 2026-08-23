#!/usr/bin/env bash
# Stop and remove the container. The Fuel cache volume survives; pass --purge
# to drop that too, at the cost of re-downloading the apartment's furniture.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
docker rm -f "$CONTAINER" >/dev/null 2>&1 && echo "removed container '$CONTAINER'" || echo "no container to remove"
if [ "${1:-}" = "--purge" ]; then
  docker volume rm "$CACHE_VOLUME" >/dev/null 2>&1 && echo "removed cache volume" || true
fi
