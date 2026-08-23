#!/usr/bin/env bash
# Build the image. Takes a few minutes and about 5 GB the first time.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
exec docker build -t "$IMAGE" "$(dirname "${BASH_SOURCE[0]}")"
