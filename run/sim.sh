#!/usr/bin/env bash
# Gazebo server + spawn + controllers + gait node. Terminal 1.
set -euo pipefail
cd "$(dirname "$0")/.."
exec pixi run bash -c 'source install/setup.bash && ros2 launch robot_cat_bringup sim.launch.py "$@"' -- "$@"
