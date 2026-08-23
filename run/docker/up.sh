#!/usr/bin/env bash
# Create the container and build the workspace inside it. Run once per session;
# it is idempotent, so re-running just restarts a stopped container.
#
#   ./run/docker/up.sh            reuse the existing container if there is one
#   ./run/docker/up.sh --recreate throw it away and start clean
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

docker image inspect "$IMAGE" >/dev/null 2>&1 \
  || die "image '$IMAGE' not found - run run/docker/build.sh first"

if [ "${1:-}" = "--recreate" ]; then
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
fi

if docker inspect "$CONTAINER" >/dev/null 2>&1; then
  docker start "$CONTAINER" >/dev/null
  echo "reusing existing container '$CONTAINER' (--recreate to start clean)"
else
  docker volume create "$CACHE_VOLUME" >/dev/null

  # Only src is bind-mounted, so colcon's build/ and install/ stay on the
  # container's own filesystem. Bind mounts onto the Windows filesystem are
  # slow enough that building through one is noticeably painful.
  mounts=(
    -v "$REPO_ROOT/src:/ws/src"
    -v "$REPO_ROOT/pytest.ini:/ws/pytest.ini:ro"
    -v "$CACHE_VOLUME:/root/.gz"
  )

  # WSLg gives a GPU-backed X server and a PulseAudio sink for free, but only
  # exists inside a WSL distro. On native Linux fall back to the host's own X
  # socket. Without either, the GUI has nowhere to draw - sim and teleop still
  # work headless.
  if [ -d /mnt/wslg ]; then
    echo "display: WSLg"
    mounts+=(
      -v /tmp/.X11-unix:/tmp/.X11-unix
      -v /mnt/wslg:/mnt/wslg
      -e "DISPLAY=${DISPLAY:-:0}"
      -e XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
      -e PULSE_SERVER=/mnt/wslg/PulseServer
    )
  elif [ -d /tmp/.X11-unix ]; then
    echo "display: host X11"
    mounts+=(-v /tmp/.X11-unix:/tmp/.X11-unix -e "DISPLAY=${DISPLAY:-:0}")
  else
    echo "display: none found - GUI will not work, sim and teleop still will"
  fi

  gpu=()
  if docker run --rm --gpus all "$IMAGE" true >/dev/null 2>&1; then
    echo "gpu: passed through"
    gpu=(--gpus all)
  else
    echo "gpu: unavailable, falling back to software rendering"
  fi

  docker run -d --name "$CONTAINER" "${gpu[@]}" "${mounts[@]}" \
    "$IMAGE" sleep infinity >/dev/null
  echo "created container '$CONTAINER'"
fi

echo "building workspace..."
docker exec "$CONTAINER" bash -c \
  'source /opt/ros/jazzy/setup.bash && cd /ws && colcon build --symlink-install'

echo
echo "ready. three terminals, same as the macOS workflow:"
echo "  ./run/docker/sim.sh      Gazebo server, the cat, controllers, gait node"
echo "  ./run/docker/gui.sh      Gazebo GUI window"
echo "  ./run/docker/teleop.sh   arrow-key teleop (needs to be the focused one)"
