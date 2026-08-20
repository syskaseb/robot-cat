#!/usr/bin/env bash
# Arrow-key teleop. Terminal 3. Needs to stay focused to receive keys.
set -euo pipefail
cd "$(dirname "$0")/.."
exec pixi run bash -c 'source install/setup.bash && ros2 run robot_cat_teleop keyboard_teleop "$@"' -- "$@"
