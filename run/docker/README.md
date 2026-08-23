# Running on Windows or Linux

The project runs natively on Apple Silicon through pixi, and `pixi.toml` pins
`platforms = ["osx-arm64"]`. On anything else `pixi install` refuses outright.
These scripts are the way in from a machine that is not that Mac: the same ROS
packages, the same launch files, the same gait, in a Linux container.

**On macOS you do not need any of this.** Use `run/sim.sh`, `run/gui.sh` and
`run/teleop.sh`, and read the Runbook in the top-level README instead. Nothing
in this directory is referenced from the macOS path, and nothing here changes
the model, the world or the gait.

## Where to run these

**From a WSL terminal**, not PowerShell and not Git Bash.

That is not a style preference. The GUI needs WSLg's X socket at
`/tmp/.X11-unix` and its runtime directory under `/mnt/wslg`, and those paths
only exist inside a WSL distribution. Run the same command from Git Bash and
Docker receives a mangled Windows path instead of the socket. Any distro will
do; the scripts do not care which.

On native Linux they work as-is from a normal terminal, falling back to the
host's own X server.

## Prerequisites

- Docker, with GPU passthrough if you want a usable frame rate. Docker
  Desktop needs **Settings → Resources → WSL Integration** enabled for the
  distro you are running from, or `docker` is simply not on the path there.
- An NVIDIA GPU is optional. `up.sh` probes for one and says which way it
  went; without it Gazebo falls back to software rendering, which works but
  is slow enough to notice.

## Use

```bash
./run/docker/build.sh     # once per machine, a few minutes and ~5 GB
./run/docker/up.sh        # create the container, build the workspace
```

Then three terminals, exactly mirroring the macOS workflow:

| terminal | command | starts |
|---|---|---|
| 1 | `./run/docker/sim.sh` | Gazebo server, the cat, controllers, gait node |
| 2 | `./run/docker/gui.sh` | Gazebo GUI window |
| 3 | `./run/docker/teleop.sh` | arrow-key teleop — needs to be focused |

`sim.sh` forwards its arguments to the launch file, so
`./run/docker/sim.sh world:=apartment_world.sdf` works the same as it does
through pixi.

`./run/docker/test.sh` runs the pure-maths suite. `./run/docker/down.sh`
removes the container; add `--purge` to drop the Fuel cache with it.

After editing anything under `src/`, re-run `./run/docker/up.sh` — it rebuilds
the workspace and reuses the existing container.

## What this environment does differently

Two things the pixi environment gets for free and Debian packaging does not,
both handled in the Dockerfile:

- **The Gazebo Python bindings** (`python3-gz-msgs10`, `python3-gz-transport13`)
  come from the OSRF repository rather than the ROS one.
  `robot_cat_teleop/camera_view.py` imports them at module scope, so without
  them the entire teleop node fails to start — not just the `v` key.
- **`GZ_SIM_SYSTEM_PLUGIN_PATH`** has to point at `/opt/ros/jazzy/lib`, because
  Gazebo only auto-searches `lib/gz-sim-8/plugins` and the packaging puts
  `libgz_ros2_control-system.so` outside it. Miss this and the server logs
  `Failed to load system plugin [gz_ros2_control-system]`, no
  `controller_manager` ever appears, and the spawners wait forever. `pixi.toml`
  works around exactly the same trap on macOS.

`m` meows through WSLg's PulseAudio sink: the image installs `paplay`, which
`robot_cat_teleop/meow.py` already looks for, so no shim is involved.

Unlike macOS, **Gazebo sensors work here** — cameras and depth sensors are not
blocked by the Cocoa main-thread restriction that stops them on the Mac. The
project does not use any yet, but this is the environment to add them in.

## Known limitation: real-time factor

The simulation runs below real time here — around 0.6 on a laptop, against
roughly 1.0 natively on the Mac. The cost is the 1 ms physics step in
`cat_world.sdf` and `apartment_world.sdf`, not the rendering and not the
furniture: a bare world measured 0.58–0.67 against the furnished world's 0.54.

Coarsening `max_step_size` would fix it and is deliberately **not** done. The
worlds are shared with the macOS setup, which does not have the problem, and
the gait's contact behaviour is tuned at 1 ms. A workaround for one platform
does not belong in a file both read.
