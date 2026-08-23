# robot cat

A 12-DOF quadruped cat simulated in Gazebo, walking with a trot gait, driven
from the laptop's arrow keys.

Runs **natively on Apple Silicon** — no Docker, no VM, no X11 — via
[RoboStack](https://robostack.github.io) (ROS 2 as conda packages).

Not on a Mac? `pixi.toml` pins `osx-arm64`, so everything below will refuse to
install. Use [`run/docker/`](run/docker/README.md) instead — same packages,
same launch files, same gait, in a Linux container.

| | |
|---|---|
| ROS 2 | Jazzy Jalisco (LTS → May 2029) |
| Gazebo | Harmonic 8.10 (LTS → May 2029) |
| Control | `ros2_control` + `gz_ros2_control` |
| Python | 3.12 (pinned by RoboStack) |

## Quick start

```bash
curl -fsSL https://pixi.sh/install.sh | bash        # once per machine
pixi install && pixi run colcon build --symlink-install
```

Then three terminals — the Gazebo server and GUI **must** be separate processes
on macOS, because Cocoa requires window creation on the main thread:

| terminal | command | starts |
|---|---|---|
| 1 | `./run/sim.sh` | Gazebo server, the cat, all four controllers, gait node |
| 2 | `./run/gui.sh` | Gazebo GUI window |
| 3 | `./run/teleop.sh` | arrow-key teleop |

With the **teleop terminal focused**:

| key | action |
|---|---|
| ↑ / ↓ | walk forwards / backwards |
| ← / → | turn left / right |
| `w` / `s` | look up / down |
| `a` / `d` | look left / right |
| space | tail one step — reverses at each end |
| `v` | cycle camera: free / third-person / first-person |
| `m` | meow |
| `x` | stretch (play-bow) |
| `p` | lie down / stand up |
| `q` | quit |

Arrows combine, so ↑ + ← walks in an arc, and the head moves independently of
the body — you can walk and look around at once. Space is a *stepped* control
rather than hold-to-move: each press nudges the tail one step, and the sweep
turns around on reaching either end. The rest pose is tail-up, so the first
press lowers it. To inspect the model on its own — no physics, joint sliders
in RViz — use `./run/display.sh`.

There is no explicit stop key: the body halts by itself within `0.25 s` of the
arrows being released.

`m` meows. Gazebo has no audio of any kind, so the clip plays through the
host (`afplay` on macOS) rather than from the simulation. The clip is a real cat,
trimmed from a public-domain Wikimedia Commons recording — provenance in
`robot_cat_teleop/sounds/SOURCE.md`.

The cat also has eyes now. They are cosmetic, but sited where a stereo pair
would really go, so camera sensors can later be mounted at the same origins.
Not on this machine though: **Gazebo cannot run camera sensors on macOS**,
because Cocoa requires render-window creation on the main thread
(gazebosim/gz-sim#960). Robotic vision means moving the runtime to Linux or
Docker; the ROS packages port over unchanged.

`x` triggers a play-bow stretch: front feet reach forward, chest drops, rear
legs straighten, held briefly, then eased back to standing. `p` toggles lying
down — all four legs fold symmetrically into a loaf — and stands back up on
the next press; a stretch cannot start while lying and pressing `p` mid-stretch
cancels it outright. Both live in `gait_controller`, not the teleop node -
the legs already belong to it - and are pure functions in
`robot_cat_gait/stretch.py` and `robot_cat_gait/lie_down.py`.

`v` cycles the viewport camera. Third-person is Gazebo's own follow, parented
behind the cat. First-person cannot use follow — follow always aims the camera
*at* its target, so it can never look out through the cat's eyes — and instead
drives the camera pose directly from the head's world pose at 20 Hz, which
means W/A/S/D turn the view exactly as they turn the head.

When you are done, kill **all three** process groups:

```bash
pkill -f "gz sim"; pkill -f gait_controller; pkill -f "ros2 launch"
```

The [Runbook](#runbook) below covers the same ground in depth, including how to
drive the cat without a keyboard and how to verify it actually walked.

## Runbook

Written for someone — or some agent — arriving at this repo cold on a macOS
machine. Every command assumes the repo root and **Apple Silicon**.

### 0. Prerequisites

`git` and [pixi](https://pixi.sh). Nothing else: no Homebrew ROS, no Docker,
no XQuartz, no system Python. Everything lives inside `.pixi/`.

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

`pixi.toml` pins `platforms = ["osx-arm64"]`. On anything else `pixi install`
fails immediately — add the platform and regenerate the lock first.

### 1. Bootstrap

```bash
pixi install && pixi run colcon build --symlink-install
```

First `pixi install` pulls ~2 GB. The build takes well under a minute. Nothing
is installed outside `.pixi/`, so removing that directory fully undoes it.

### 2. Prove the logic before starting anything heavy

```bash
pixi run pytest
```

581 tests in under a second — pure maths, no simulator and no ROS runtime.
If these fail, do not bother launching Gazebo; the gait or IK is broken.

### 3. Run it

Everything must run inside the pixi environment, and ROS needs its overlay
sourced on top. That is what the `run/` wrappers exist for:

| terminal | command | what it starts |
|---|---|---|
| 1 | `./run/sim.sh` | Gazebo **server**, spawns the cat, all four controllers, gait node |
| 2 | `./run/gui.sh` | Gazebo **GUI** window |
| 3 | `./run/teleop.sh` | arrow-key teleop — needs to be the focused window |

The server and GUI are deliberately separate processes. macOS requires window
creation on the main thread, so a combined `gz sim` cannot work here.

By default the cat spawns in the bare `cat_world.sdf` test arena. For a living
room + open kitchen to walk around instead, pass a world argument:

```bash
./run/sim.sh world:=apartment_world.sdf
```

The furniture (OpenRobotics' Fuel-hosted "Kitchen and Dining" and "Sofa"
models, both CC0) is visual only — no collision — so the cat can cross the
floor freely but will walk through the counter rather than bump it.

### 4. Wait for readiness — do not guess with `sleep`

Startup is around 10 s on Cyclone (it was 30–40 s on the Fast DDS default,
when it came up at all). Poll rather than sleeping:

```bash
until pixi run bash -c 'source install/setup.bash >/dev/null 2>&1; ros2 control list_controllers 2>/dev/null | grep -q "leg_position_controller.*active"'; do sleep 5; done
```

All four of `joint_state_broadcaster`, `leg_position_controller`,
`head_position_controller` and `tail_position_controller` must report
`active`. If `controller_manager` never appears, the `gz_ros2_control` plugin
failed to load — check `GZ_SIM_SYSTEM_PLUGIN_PATH` under "macOS specifics".

### 5. Driving it without a keyboard

`teleop.sh` reads a real terminal, so it is useless to an automated caller.
Publish to `/cmd_vel` directly instead — same interface the teleop node uses:

```bash
pixi run bash -c 'source install/setup.bash && ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.15}, angular: {z: 0.6}}" -r 20'
```

Stop publishing and the watchdog returns the cat to a stance within 0.5 s.

### 6. Verify it actually walked

Do not trust the viewport — read the pose:

```bash
pixi run bash -c 'source install/setup.bash && gz model -m robot_cat -p'
```

A healthy standing cat sits at `z ≈ 0.172` with roll and pitch near zero. To
confirm motion, sample the pose before and after a `/cmd_vel` burst.

### 7. Shut down properly

```bash
pkill -f "gz sim"; pkill -f gait_controller; pkill -f "ros2 launch"
```

**All three.** See the first gotcha below for why.

### Gotchas that will otherwise cost you an hour

- **`pkill -f "ros2 launch"` alone leaves orphans.** It kills the launcher, not
  its child nodes. Two surviving `gait_controller` processes publish to the same
  command topic at 100 Hz each, with independent gait phases, and the cat skates
  across the world looking like a physics bug. Always check
  `pgrep -fl gait_controller` before diagnosing strange motion.
- **Never `set -u` before `source install/setup.bash`.** colcon's script reads
  unset variables and aborts the whole shell.
- **Parsing `gz model -p`: use `tr -d '[]'`, not `tr -d ' []'`.** Stripping
  spaces concatenates the three coordinates into one unreadable number.
- **Yaw wraps at ±π.** A 10 s turn easily exceeds half a revolution, so a
  "backwards" reading is usually a wrap, not a bug. Measure turn rates with
  bursts of ~4 s.
- **Commanded speed is not achieved speed.** The gait is open loop and the paws
  slip; expect roughly 0.11–0.17 m/s for a 0.15 m/s command, varying run to run.
- **Top speed is structural**, at `max_stride / cycle_time` = 0.53 m/s. Higher
  commands are clamped, not obeyed.
- **A cat that walks lame is a dropped-message problem, not a gait problem.**
  If it stutters, veers tens of degrees off a straight command, or barely
  moves while the head and tail still respond perfectly, read the sim log:

  ```bash
  grep "holding stance" /tmp/<your sim log>
  ```

  Repeated `no /cmd_vel for 1.7s - holding stance` means the gait watchdog is
  firing mid-stride because `/cmd_vel` is not arriving, and the legs stop
  dead. The head and tail keep working throughout, because a plain position
  setpoint does not care about a dropped message - that asymmetry is the
  giveaway. The cause was Fast DDS's shared-memory transport; this repo runs
  Cyclone instead, see `config/cyclonedds_localhost.xml`.
- **Killing a `ros2 topic pub` is harder than it looks.** Backgrounding
  `pixi run bash -c '... ros2 topic pub ...'` and sending `kill -INT $!` kills
  only the wrapper — the real publisher is a *grandchild* python process and
  survives, quietly driving `/cmd_vel` at 20 Hz forever. The cat then walks
  off on its own and every later measurement is wrong. Always verify with
  `pgrep -fl "ros2 topic pub"` afterwards, and clear stragglers with
  `pkill -9 -f "ros2 topic pub"`.

## Layout

```
src/robot_cat_description/   URDF/xacro model, ros2_control wiring, controller config
src/robot_cat_gait/          trot gait + leg IK (pure maths) and the ROS node
src/robot_cat_teleop/        arrow-key teleop, head and tail control
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
                    |                             |
                    |               trot phase + per-leg IK
                    |                             |
                    |               /leg_position_controller/commands
   w a s d, space   |                             |
                    +-> /head_position_controller/commands
                    +-> /tail_position_controller/commands
                                                  |
                            ros2_control -> gz_ros2_control -> Gazebo
```

The head and tail bypass the gait entirely: they are cosmetic joints with
their own smoothing (`head.py`, `tail.py`), published straight from the teleop
node at its own 20 Hz, so looking around never perturbs the walk.

`gait_controller` is open loop: it converts a velocity command into foot
trajectories and joint angles, with no feedback from the robot's actual pose.
It holds a neutral stance when no `/cmd_vel` arrives for 0.5 s, so the cat stops
if teleop dies.

## Measured behaviour

From Gazebo, driving `/cmd_vel` directly (see "Tuning" for what moves these).
**These figures pre-date `stance_width`** and were taken on macOS with the
paws directly under the hips; the splay makes the cat noticeably faster, so
the forward row in particular now reads low. They have not been re-taken on
that machine — the `stance_width` table in `gait.py` has the numbers that
motivated the change, measured under Docker where the real-time factor sits
around 0.6.

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
  `max_stride / cycle_time` = 0.53 m/s. Commanding more is clamped rather than
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
- **`cycle_time`** (0.3 s) — one full gait cycle. On the original short legs,
  anything under 0.5 measurably worsened heading drift; the 0.11 m legs moved
  that trade, and 0.3 is measured at 0.58–0.64 m/s with the same ~1 °/m drift.
  Retune it together with `max_stride` — the table in `gait.py` shows why one
  without the other goes backwards.
- **`stance_height`** (0.16 m) — hip-to-paw distance. Lower is more stable, but
  it is tied to `thigh_length`/`calf_length`: what the gait cares about is how
  far the knee stays bent, so move all three together or the leg straightens.
- **`stance_width`** (0.02 m) — how far the paws splay outside the hips. At 0
  the IK solves every hip roll joint to exactly zero, so four of the twelve
  motors never move and the cat wallows 8–11° in roll. 0.02 cuts that to 2–4°
  and, because a steady body slips less, roughly doubles achieved speed. See
  the measured table in `gait.py`.
- **`max_stride`** (0.16 m) — caps how far the IK is asked to reach. A longer
  stride at a slow tempo is *slower* — near full extension the leg shears
  instead of pushing — so treat this and `cycle_time` as one knob.

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

4. **`RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` plus `CYCLONEDDS_URI`** — Fast
   DDS, the ROS default, cannot use shared memory here: its lock files under
   `/tmp/boost_interprocess` go stale whenever a node is killed rather than
   shut down, and it responds by silently dropping traffic instead of
   failing. That is what makes the cat walk lame. Forcing Fast DDS onto UDP
   alone does not help - the same VPN that owns the multicast range breaks
   its discovery. `config/cyclonedds_localhost.xml` has the full write-up.

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
