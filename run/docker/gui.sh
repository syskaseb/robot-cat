#!/usr/bin/env bash
# Gazebo GUI window. Terminal 2.
#
# Separate from the server for the same reason as on macOS, though for a
# different cause: there the split is forced by Cocoa, here `gz sim` in one
# process simply gives the container no way to hand a window to the host.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_container
docker exec "$CONTAINER" sh -c '[ -d /mnt/wslg ] || [ -d /tmp/.X11-unix ]' \
  || die "no display was mounted when the container was created - see run/docker/README.md"

# shellcheck disable=SC2046  # deliberate word splitting of the flag list
docker exec $(tty_flags) "$CONTAINER" \
  bash -c "source /opt/ros/jazzy/setup.bash && gz sim -g"
