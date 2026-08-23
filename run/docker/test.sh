#!/usr/bin/env bash
# The pure-maths suite, no simulator. Same tests `pixi run pytest` runs.
#
# test_camera_view.py needs the Gazebo Python bindings, which the image does
# install - if this errors on `No module named gz`, the image predates them
# and needs run/docker/build.sh again.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
in_container "cd /ws && python3 -m pytest -c pytest.ini $*"
