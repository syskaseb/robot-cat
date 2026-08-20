#!/usr/bin/env bash
# RViz + joint sliders, no physics. For checking the model itself.
set -euo pipefail
cd "$(dirname "$0")/.."
exec pixi run bash -c 'source install/setup.bash && ros2 launch robot_cat_bringup display.launch.py'
