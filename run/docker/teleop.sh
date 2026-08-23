#!/usr/bin/env bash
# Arrow-key teleop. Terminal 3. Needs to stay focused to receive keys.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
in_container "ros2 run robot_cat_teleop keyboard_teleop $*"
