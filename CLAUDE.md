# robot cat — notes for Claude

Quadruped robot cat: ROS 2 Jazzy + Gazebo Harmonic, running **natively on
macOS / Apple Silicon** through RoboStack (conda packages, driven by `pixi`).

**Read the Runbook section of [README.md](README.md) before running anything.**
It covers bootstrap, startup, how to drive the cat without a keyboard, and how
to verify it actually walked. What follows is only the part most likely to
waste your time.

## Environment

There is no system ROS. Every command must go through pixi:

```bash
pixi run bash -c 'source install/setup.bash && <ros2 command>'
```

Plain `ros2 ...` will not be found, and `source install/setup.bash` alone is not
enough — the overlay sits on top of the pixi environment, not instead of it.

## Rules that are easy to get wrong

- **Never `set -u` before `source install/setup.bash`.** colcon's script reads
  unset variables and aborts the whole shell. This looks like the launch failing
  for no reason.
- **Shut down with all three:**
  `pkill -f "gz sim"; pkill -f gait_controller; pkill -f "ros2 launch"`.
  Killing only the launcher orphans its child nodes. Two surviving
  `gait_controller` processes publish to the same command topic at 100 Hz with
  independent gait phases, and the cat skates across the world looking exactly
  like a physics bug. Check `pgrep -fl gait_controller` before diagnosing any
  strange motion.
- **Startup takes ~10 s.** Poll until all four controllers report `active`
  rather than sleeping a fixed amount — see Runbook step 4.
- **A lame-looking cat is dropped `/cmd_vel`, not a broken gait.** Stuttering,
  tens of degrees of veer, or barely moving *while the head and tail still
  respond* means the 0.5 s gait watchdog is firing mid-stride. Check
  `grep "holding stance"` in the sim log. This is why the repo pins
  `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`; Fast DDS's shared memory is broken
  on this machine and drops traffic silently. See
  `config/cyclonedds_localhost.xml`.
- **`kill -9` on a `ros2 topic pub` leaves a ghost publisher** in discovery
  that the next run inherits. Use `kill -INT` and wait.
- **`teleop.sh` publishes `/cmd_vel` at 20 Hz even when idle** (zeros). Do not
  run it while driving `/cmd_vel` from the CLI — the two publishers interleave
  and the cat barely moves.
- **You cannot use the keyboard teleop.** It reads an interactive terminal.
  Publish to `/cmd_vel` instead; it is the same interface the teleop node uses.
- **Verify motion by reading the pose**, not the viewport:
  `gz model -m robot_cat -p`. Standing height is `z ≈ 0.142`. Parse it with
  `tr -d '[]'` — including a space in that set concatenates the coordinates.
- **Yaw wraps at ±π.** A "backwards" turn reading after a long spin is almost
  always a wrap. Measure turn rates in bursts of ~4 s.

## Layout

| package | contents |
|---|---|
| `robot_cat_description` | xacro model, `ros2_control` wiring, controller config |
| `robot_cat_gait` | leg IK and trot generation (ROS-free, unit tested) + the node |
| `robot_cat_teleop` | arrow-key body teleop, W/A/S/D head, space-stepped tail, `v` camera views; decoding, head easing, tail sweep and the first-person pose maths are pure functions in `keys.py`, `head.py`, `tail.py`, `camera_view.py` |
| `robot_cat_bringup` | world, launch files, RViz config |

## Changing things

The gait maths is pure and fully unit tested — `pixi run pytest` is 519 tests in
under a second, with no simulator. Run it before launching Gazebo; if it fails,
the simulator will only obscure the cause.

Gait defaults were chosen by measurement, not taste, and the reasoning is
recorded in `gait.py` docstrings. Before "improving" `duty_factor` or
`cycle_time`, read those — a textbook 0.5 trot drifts 12x more in heading.

Link lengths are duplicated by design: `cat.urdf.xacro` and `LegGeometry` in
`leg_ik.py` are not derived from one another. Change one, change the other.

## Known limitation

Gazebo **sensors do not work on macOS** — cameras, lidar and depth sensors crash
because Cocoa requires render-window creation on the main thread
(gazebosim/gz-sim#960). Nothing here needs them. Adding perception means moving
the runtime to Docker or Linux; the ROS packages port over unchanged.
