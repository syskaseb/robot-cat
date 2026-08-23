#!/usr/bin/env bash
# Arrow-key teleop. Terminal 3. Needs to stay focused to receive keys.
#
# Unlike the other scripts here this one insists on a real terminal rather
# than degrading quietly. keyboard_teleop reads the raw file descriptor, so
# without a TTY it prints its own refusal and exits immediately - which looks
# like the container being broken rather than the way it was launched.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_container

[ -t 0 ] || die "no terminal on stdin - run this directly in a terminal window.
  Piping it (even through 'tee') or launching it from a script takes the TTY
  away, and the teleop cannot read arrow keys without one."

exec docker exec -it "$CONTAINER" bash -c \
  "source /opt/ros/jazzy/setup.bash && source /ws/install/setup.bash && ros2 run robot_cat_teleop keyboard_teleop $*"
