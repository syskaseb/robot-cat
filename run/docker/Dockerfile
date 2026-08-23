# ROS 2 Jazzy + Gazebo Harmonic on Ubuntu Noble.
#
# This is the Linux/Windows path into the project. It exists because pixi.toml
# pins osx-arm64, so `pixi install` refuses to run anywhere else - see
# run/docker/README.md. On an Apple Silicon Mac you do not need any of this.
#
# The apt packages here are the same set RoboStack provides through pixi, with
# two additions the pixi environment gets for free and Debian packaging does
# not:
#
#   python3-gz-msgs10 / python3-gz-transport13 - the Gazebo Python bindings.
#     robot_cat_teleop/camera_view.py imports them at module scope, so without
#     these the whole teleop node fails to start, not just the `v` key.
#     They live in the OSRF repo rather than the ROS one, hence the extra key.
#
#   pulseaudio-utils - supplies `paplay`, which is already one of the players
#     robot_cat_teleop/meow.py looks for. Pointed at WSLg's PulseServer it
#     makes `m` audible on the Windows host with no shim of our own.
FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      gnupg \
      lsb-release \
 && curl -fsSL https://packages.osrfoundation.org/gazebo.gpg \
      -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
      > /etc/apt/sources.list.d/gazebo-stable.list \
 && apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      cmake \
      ninja-build \
      pkg-config \
      python3-colcon-common-extensions \
      python3-pytest \
      python3-gz-msgs10 \
      python3-gz-transport13 \
      pulseaudio-utils \
      ros-jazzy-gz-ros2-control \
      ros-jazzy-ros-gz \
      ros-jazzy-ros2-controllers \
      ros-jazzy-ros2controlcli \
      ros-jazzy-xacro \
 && rm -rf /var/lib/apt/lists/*

# Gazebo only auto-searches lib/gz-sim-8/plugins, but the Debian packaging puts
# libgz_ros2_control-system.so straight into /opt/ros/jazzy/lib. Without this
# the server reports "Failed to load system plugin [gz_ros2_control-system]"
# and no controller_manager ever appears - the same trap pixi.toml works around
# with GZ_SIM_SYSTEM_PLUGIN_PATH on macOS.
ENV GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ros/jazzy/lib

WORKDIR /ws
