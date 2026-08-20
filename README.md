# robot cat

A 12-DOF quadruped cat simulated in Gazebo, walking with a trot gait, driven
from the laptop's arrow keys.

Runs **natively on Apple Silicon** — no Docker, no VM, no X11 — via
[RoboStack](https://robostack.github.io) (ROS 2 as conda packages).

| | |
|---|---|
| ROS 2 | Jazzy Jalisco (LTS → May 2029) |
| Gazebo | Harmonic 8.10 (LTS → May 2029) |
| Control | `ros2_control` + `gz_ros2_control` |
| Python | 3.12 (pinned by RoboStack) |

## Setup

Once, to install [pixi](https://pixi.sh):

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

Then, in this directory:

```bash
pixi install && pixi run colcon build --symlink-install
```

## Running

Three terminals. The Gazebo server and GUI **must** be separate processes on
macOS — Cocoa requires window creation on the main thread, so a combined
`gz sim` cannot work here.

```bash
./run/sim.sh
```

```bash
./run/gui.sh
```

```bash
./run/teleop.sh
```

Then, with the **teleop terminal focused**:

| key | action |
|---|---|
| ↑ / ↓ | walk forwards / backwards |
| ← / → | turn left / right |
| space | stop |
| `q` | quit |

Arrows combine, so ↑ + ← walks in an arc.

To inspect the model on its own — no physics, joint sliders in RViz:

```bash
./run/display.sh
```

## Layout

```
src/robot_cat_description/   URDF/xacro model, ros2_control wiring, controller config
src/robot_cat_gait/          trot gait + leg IK (pure maths) and the ROS node
src/robot_cat_teleop/        arrow-key teleop
src/robot_cat_bringup/       world, launch files, RViz config
run/                         thin wrappers around the three commands above
```

The interesting maths is in `robot_cat_gait/leg_ik.py` (analytic 3-DOF IK) and
`gait.py` (trot phase and foot trajectories). Both are ROS-free and unit tested,
so you can tune the gait without launching a simulator:

```bash
pixi run pytest
```

## How it fits together

```
arrow keys -> keyboard_teleop -> /cmd_vel -> gait_controller
                                                  |
                                    trot phase + per-leg IK
                                                  |
                                    /leg_position_controller/commands
                                                  |
                            ros2_control -> gz_ros2_control -> Gazebo
```

`gait_controller` is open loop: it converts a velocity command into foot
trajectories and joint angles, with no feedback from the robot's actual pose.
It holds a neutral stance when no `/cmd_vel` arrives for 0.5 s, so the cat stops
if teleop dies.

## Measured behaviour

From Gazebo, driving `/cmd_vel` directly (see "Tuning" for what moves these):

| command | result |
|---|---|
| forward 0.15 m/s, 8 s | 0.94 m travelled, **1.0° heading drift** |
| backward 0.15 m/s, 8 s | 0.54 m — reverse is slower, the paws slip more |
| spin ±0.8 rad/s, 4 s | turns in place, **< 1 cm** of position drift |
| arc 0.15 m/s + 0.6 rad/s | curves correctly both ways, ~0.4 m radius |
| stop publishing `/cmd_vel` | halts within 0.5 s and holds stance exactly |

Two honest caveats:

- **The gait is open loop.** It converts a velocity command into foot
  trajectories; nothing measures where the cat actually ended up. Achieved
  speed runs below commanded (roughly 0.11–0.17 m/s for a 0.15 m/s command)
  because the paws slip, and it varies between runs — legged contact is
  stochastic. Closing the loop would need odometry or an IMU.
- **Top speed is structural**: one stride per cycle, so
  `max_stride / cycle_time` = 0.16 m/s. Commanding more is clamped rather than
  silently saturated.

## Tuning

Every gait parameter is a ROS parameter, so you can retune live:

```bash
ros2 param set /gait_controller stance_height 0.11
```

The ones that matter most, in order:

- **`duty_factor`** (0.65) — fraction of the cycle each foot is on the ground.
  The single biggest lever on whether the cat walks straight. See the table in
  `gait.py`; 0.5 is a textbook trot and drifts 12× more in heading.
- **`cycle_time`** (0.5 s) — one full gait cycle. Shorter is not faster; it
  measurably worsened heading drift.
- **`stance_height`** (0.13 m) — hip-to-paw distance. Lower is more stable.
- **`max_stride`** (0.08 m) — caps how far the IK is asked to reach.

If you change a **link length**, change it in *both*
`robot_cat_description/urdf/cat.urdf.xacro` and `LegGeometry` in
`robot_cat_gait/leg_ik.py`. They are not derived from one another.

## macOS specifics

Three things this repo configures that a Linux setup would not need. All live
in `[activation.env]` in `pixi.toml`:

1. **`GZ_IP=127.0.0.1`** — this machine's VPN (`utun4`) claims the whole
   `224.0.0.0/4` multicast range, including gz-transport's discovery address
   `239.255.0.7`. Without pinning to loopback, Gazebo dies with
   `Exception sending a multicast message: No route to host`.
2. **`GZ_SIM_SYSTEM_PLUGIN_PATH=$CONDA_PREFIX/lib`** — Gazebo only auto-searches
   `lib/gz-sim-8/plugins`, but RoboStack installs
   `libgz_ros2_control-system.dylib` into `lib`. Without this you get
   `Failed to load system plugin [gz_ros2_control-system]` and no
   `controller_manager` ever appears.
3. **`ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`** — same VPN problem for DDS, and
   it keeps ROS traffic off the corporate network.

`pytest.ini` disables the `launch_testing` plugins: RoboStack's copies are built
against an older pytest and abort collection on import.

### Known limitation

**Gazebo sensors do not work on macOS** — cameras, lidar and depth sensors crash,
because Cocoa requires render-window creation on the main thread
([gz-sim#960](https://github.com/gazebosim/gz-sim/issues/960)). Nothing here needs
them: the gait is pure joint-position control. Adding perception later means
moving the runtime to Docker or a Linux VM; the ROS packages port over unchanged.

## Troubleshooting

**The Gazebo window is empty / I can't find the cat.** The cat is 30 cm long;
Gazebo's stock camera sits ~6 m back and renders it as a speck. `cat_world.sdf`
declares its own `<gui>` block with the camera 1.5 m out. Note that declaring
`<gui>` at all replaces Gazebo's defaults wholesale, so every panel you want
has to be listed there — that is why `Screenshot` and `TransformControl` appear
explicitly.

**Arrow keys do nothing.** First check the teleop terminal is focused. If it
still does nothing, it is not a focus problem — see `robot_cat_teleop/keys.py`.
Two things bite here, and both fail *silently*:

- Terminals send `ESC [ A` in normal cursor-key mode but `ESC O A` in
  application mode, and switch between them freely. Both are decoded.
- Input must be read from the raw file descriptor with `os.read`. Reading via
  `sys.stdin.read(1)` pulls the whole three-byte sequence into Python's own
  buffer, after which `select()` on the descriptor reports nothing pending and
  the rest of the sequence is lost — which looks exactly like the arrow keys
  being ignored.

**The cat walks by itself, or twitches oddly.** Check for orphaned nodes:

```bash
pgrep -fl gait_controller
```

`pkill -f "ros2 launch"` kills the launcher but leaves its child nodes running.
Two gait controllers publishing to the same command topic at 100 Hz each will
make the cat skate across the world.

## PyCharm

Set the project interpreter to `.pixi/envs/default/bin/python` for completion on
`rclpy` and the generated message types.
