# robot cat — notes for Claude

Quadruped robot cat: ROS 2 Jazzy + Gazebo Harmonic, running **natively on
macOS / Apple Silicon** through RoboStack (conda packages, driven by `pixi`).

**Read the Runbook section of [README.md](README.md) before running anything.**
It covers bootstrap, startup, how to drive the cat without a keyboard, and how
to verify it actually walked. What follows is only the part most likely to
waste your time.

## Environment

**Check which platform you are on before running anything.** On macOS the
project runs through pixi, as below. On Windows or Linux `pixi install` refuses
outright — `pixi.toml` pins `osx-arm64` — and the way in is
`run/docker/`, which has its own README. The two paths share every source file,
so a change made in one has to keep working in the other; nothing
platform-specific belongs in `src/`.

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
- **A backgrounded `ros2 topic pub` outlives `kill -INT $!`.** The pid you
  captured is the `pixi run` wrapper; the publisher itself is a grandchild
  python process and keeps driving `/cmd_vel` at 20 Hz, so the cat walks off
  by itself and later measurements are garbage. Always confirm with
  `pgrep -fl "ros2 topic pub"` and clear with `pkill -9 -f "ros2 topic pub"`.
- **`teleop.sh` publishes `/cmd_vel` at 20 Hz even when idle** (zeros). Do not
  run it while driving `/cmd_vel` from the CLI — the two publishers interleave
  and the cat barely moves.
- **You cannot use the keyboard teleop.** It reads an interactive terminal.
  Publish to `/cmd_vel` instead; it is the same interface the teleop node uses.
- **Verify motion by reading the pose**, not the viewport:
  `gz model -m robot_cat -p`. Standing height is `z ≈ 0.172`. Parse it with
  `tr -d '[]'` — including a space in that set concatenates the coordinates.
- **Yaw wraps at ±π.** A "backwards" turn reading after a long spin is almost
  always a wrap. Measure turn rates in bursts of ~4 s.

## Layout

| package | contents |
|---|---|
| `robot_cat_description` | xacro model, `ros2_control` wiring, controller config |
| `robot_cat_gait` | leg IK, trot generation, the play-bow stretch and the lie-down loaf (all ROS-free, unit tested) + the node, which also owns `/stretch` and `/lie_down` |
| `robot_cat_teleop` | arrow-key body teleop, W/A/S/D head, space-stepped tail, `v` camera views, `m` meow, `x`/`p` requests to the gait node; decoding, head easing, tail sweep and the first-person pose maths are pure functions in `keys.py`, `head.py`, `tail.py`, `camera_view.py` |
| `robot_cat_bringup` | world, launch files, RViz config |

## Changing things

The gait maths is pure and fully unit tested — `pixi run pytest` is 581 tests in
under a second, with no simulator. Run it before launching Gazebo; if it fails,
the simulator will only obscure the cause.

Gait defaults were chosen by measurement, not taste, and the reasoning is
recorded in `gait.py` docstrings. Before "improving" `duty_factor` or
`cycle_time`, read those — a textbook 0.5 trot drifts 12x more in heading.

Link lengths are duplicated by design: `cat.urdf.xacro` and `LegGeometry` in
`leg_ik.py` are not derived from one another. Change one, change the other —
and `gait_controller.py` declares them a third time as ROS parameter defaults,
so that is three files, not two.

The leg is sized for **proportion**, not just reach. Segments are `0.11` and
the cat stands at `0.16`, which puts the withers at 21.7 cm over a 22 cm hip
span — near enough square, which is what reads as feline. The earlier `0.09`
segments at `0.13` gave a ratio of 0.85 and looked like a dachshund. Those two
numbers move **together**: what the gait actually depends on is the knee
staying near 73% of full reach, and raising `stance_height` on its own
straightens it toward a locked leg with no swing clearance.

`stance_width` is not cosmetic. Setting it to 0 puts each paw in the plane of
its own hip, which makes `leg_ik` solve that roll joint to exactly zero for
every pose — four of the twelve motors stop moving entirely and the cat
wallows about 8–11° in roll on the diagonal it is standing on. Every lateral
offset in `GaitGenerator` goes through `_neutral_y()` so that walking,
standing, stretching and lying down widen together and
`stretch_pose(0) == stand()` stays true; if you add another pose, use it
rather than `hip_offset` directly.

All four legs bend the **same** way. An earlier revision mirrored the rear
knees to be anatomically catlike; that was deliberately reverted to match how
real quadruped robots (Spot, Unitree) are actually built, with four identical
legs. `knee_sign` still selects the IK branch, but it is now one value for the
whole robot.

## Known limitation

Gazebo **sensors do not work on macOS** — cameras, lidar and depth sensors crash
because Cocoa requires render-window creation on the main thread
(gazebosim/gz-sim#960). Nothing here needs them. Adding perception means moving
the runtime to Docker or Linux; the ROS packages port over unchanged.
