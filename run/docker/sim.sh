#!/usr/bin/env bash
# Gazebo server + spawn + controllers + gait node. Terminal 1.
# Mirrors run/sim.sh, which does the same thing through pixi on macOS.
#
#   ./run/docker/sim.sh                              bare test arena
#   ./run/docker/sim.sh world:=apartment_world.sdf   flat with furniture
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
in_container "ros2 launch robot_cat_bringup sim.launch.py $*"
