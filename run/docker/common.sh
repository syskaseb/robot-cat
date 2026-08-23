#!/usr/bin/env bash
# Shared settings and helpers. Sourced by the other scripts here, not run.
set -euo pipefail

IMAGE=${ROBOT_CAT_IMAGE:-robot-cat:jazzy}
CONTAINER=${ROBOT_CAT_CONTAINER:-robot-cat}

# Gazebo re-downloads the Fuel models the apartment world includes on every
# fresh container otherwise, and a failed download takes the whole world down
# rather than just the sofa. A named volume keeps the cache across `down.sh`.
CACHE_VOLUME=${ROBOT_CAT_CACHE_VOLUME:-robot-cat-gz-cache}

# Repo root, however deep this script was invoked from.
REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)

die() { echo "error: $*" >&2; exit 1; }

require_container() {
  docker inspect "$CONTAINER" >/dev/null 2>&1 \
    || die "container '$CONTAINER' does not exist - run run/docker/up.sh first"
  [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER")" = "true" ] \
    || die "container '$CONTAINER' is not running - run run/docker/up.sh first"
}

# `docker exec -it` fails outright with "the input device is not a TTY" when
# there is no terminal, which is every CI job and every scripted smoke test.
# The teleop genuinely needs the TTY; the rest only want it for readable
# output, so ask for it when it exists and carry on when it does not.
tty_flags() {
  if [ -t 0 ] && [ -t 1 ]; then echo "-it"; else echo "-i"; fi
}

# Everything inside the container needs the ROS environment plus this
# workspace's overlay. Never `set -u` before sourcing setup.bash: colcon's
# script reads unset variables and aborts the whole shell.
in_container() {
  require_container
  # shellcheck disable=SC2046  # deliberate word splitting of the flag list
  docker exec $(tty_flags) "$CONTAINER" bash -c \
    "source /opt/ros/jazzy/setup.bash && source /ws/install/setup.bash && $1"
}
