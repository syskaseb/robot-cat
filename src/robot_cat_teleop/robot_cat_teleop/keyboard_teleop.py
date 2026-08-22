"""ROS 2 node: drive the cat with the arrow keys.

``teleop_twist_keyboard`` is bound to ``i``/``j``/``k``/``l``, so this is a
purpose-built node for the arrow keys. The decoding itself lives in
:mod:`robot_cat_teleop.keys`.

Because keyboards send an autorepeat stream rather than a held-down signal,
"key is held" is inferred from how recently the last repeat arrived: the
commanded velocity decays to zero shortly after the key is released.
"""

from __future__ import annotations

import atexit
import os
import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

from .camera_view import CameraController, CameraView
from .head import HeadParams, HeadState
from .keys import CAMERA_CYCLE, MEOW, QUIT, TAIL_STEP, decode_keys
from .meow import Meower
from .tail import TailParams, TailState

HELP = """
robot cat teleop
----------------
  up / down     walk forwards / backwards
  left / right  turn left / right
  w / s         look up / down
  a / d         look left / right
  space         tail one step - reverses at each end
  v             cycle camera: free / third-person / first-person
  m             meow
  q or Ctrl-C   quit

Hold a key to keep moving. Keep this terminal focused.
"""

_VIEW_LABEL = {
    CameraView.FREE: "free (mouse control)",
    CameraView.THIRD_PERSON: "third-person",
    CameraView.FIRST_PERSON: "first-person (head cam)",
}




class KeyboardTeleop(Node):
    def __init__(self) -> None:
        super().__init__("keyboard_teleop")

        # Just inside what the gait can deliver (0.16 m/s, 1.13 rad/s for the
        # default geometry) so a held key produces steady motion rather than a
        # saturated command.
        self.declare_parameter("linear_speed", 0.15)
        self.declare_parameter("angular_speed", 1.0)
        self.declare_parameter("publish_rate", 20.0)
        self.declare_parameter("key_hold_timeout", 0.25)

        # --- head (W/A/S/D) tunables - see robot_cat_teleop.head for why a
        # velocity filter rather than a direct angle makes this look alive.
        self.declare_parameter("head_pan_range", [-0.6, 0.6])
        self.declare_parameter("head_tilt_range", [-0.3, 0.5])
        self.declare_parameter("head_max_rate", 1.4)
        self.declare_parameter("head_velocity_tau", 0.12)
        self.declare_parameter("head_command_topic", "/head_position_controller/commands")

        # --- tail (space) tunables - see robot_cat_teleop.tail.
        self.declare_parameter("tail_range", [-1.2, 0.9])
        self.declare_parameter("tail_step", 0.3)
        self.declare_parameter("tail_tau", 0.10)
        # Autorepeat fires ~30 times a second while space is held, which would
        # otherwise blur the whole sweep into a flap. One step per interval
        # turns a held key into a steady sweep and leaves a tap as one step.
        self.declare_parameter("tail_press_interval", 0.18)
        self.declare_parameter("tail_command_topic", "/tail_position_controller/commands")

        self._lin = float(self.get_parameter("linear_speed").value)
        self._ang = float(self.get_parameter("angular_speed").value)
        self._hold = float(self.get_parameter("key_hold_timeout").value)
        rate = float(self.get_parameter("publish_rate").value)

        pan_lower, pan_upper = self.get_parameter("head_pan_range").value
        tilt_lower, tilt_upper = self.get_parameter("head_tilt_range").value
        self._head = HeadState(
            HeadParams(
                pan_lower=float(pan_lower),
                pan_upper=float(pan_upper),
                tilt_lower=float(tilt_lower),
                tilt_upper=float(tilt_upper),
                max_rate=self._f("head_max_rate"),
                velocity_tau=self._f("head_velocity_tau"),
            )
        )

        tail_min, tail_max = self.get_parameter("tail_range").value
        self._tail = TailState(
            TailParams(
                min_angle=float(tail_min),
                max_angle=float(tail_max),
                step=self._f("tail_step"),
                tau=self._f("tail_tau"),
            )
        )
        self._tail_interval = self._f("tail_press_interval")
        self._last_tail_press = 0.0

        self._pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self._head_pub = self.create_publisher(
            Float64MultiArray, self.get_parameter("head_command_topic").value, 10
        )
        self._tail_pub = self.create_publisher(
            Float64MultiArray, self.get_parameter("tail_command_topic").value, 10
        )
        self._pressed: dict[str, float] = {}
        self._quit = False
        self._last_tick = self._now()
        self._timer = self.create_timer(1.0 / rate, self._tick)
        self._camera = CameraController()
        self._meower = Meower()

    def _f(self, name: str) -> float:
        return float(self.get_parameter(name).value)

    def note_key(self, key: str) -> None:
        self._pressed[key] = self._now()

    def step_tail(self) -> None:
        """One space press. Ignored if it lands inside the repeat interval."""
        now = self._now()
        if now - self._last_tail_press < self._tail_interval:
            return
        self._last_tail_press = now
        self._tail.press()

    def cycle_camera(self) -> None:
        view = self._camera.cycle()
        print(f"camera: {_VIEW_LABEL[view]}")

    def meow(self) -> None:
        if not self._meower.available:
            print("no audio player found - cannot meow")
            return
        self._meower.meow(self._now())

    def shutdown_camera(self) -> None:
        try:
            self._camera.shutdown()
        except Exception:
            pass

    def request_quit(self) -> None:
        self._quit = True

    @property
    def quit_requested(self) -> bool:
        return self._quit

    def _now(self) -> float:
        return self.get_clock().now().nanoseconds * 1e-9

    def _held(self, key: str) -> bool:
        last = self._pressed.get(key)
        return last is not None and (self._now() - last) < self._hold

    def _tick(self) -> None:
        now = self._now()
        dt = now - self._last_tick
        self._last_tick = now
        # Guard against a zero or absurd dt on the first tick or a sim-time
        # jump, same reasoning as gait_controller._tick.
        if dt <= 0.0 or dt > 0.5:
            dt = 1.0 / float(self.get_parameter("publish_rate").value)

        twist = Twist()
        if self._held("up"):
            twist.linear.x = self._lin
        elif self._held("down"):
            twist.linear.x = -self._lin
        if self._held("left"):
            twist.angular.z = self._ang
        elif self._held("right"):
            twist.angular.z = -self._ang
        self._pub.publish(twist)

        pan_dir = 0.0
        if self._held("head_left"):
            pan_dir = 1.0
        elif self._held("head_right"):
            pan_dir = -1.0
        tilt_dir = 0.0
        if self._held("head_up"):
            tilt_dir = 1.0
        elif self._held("head_down"):
            tilt_dir = -1.0

        pan, tilt = self._head.step(dt, pan_dir, tilt_dir)
        head_msg = Float64MultiArray()
        head_msg.data = [pan, tilt]
        self._head_pub.publish(head_msg)

        tail_msg = Float64MultiArray()
        tail_msg.data = [self._tail.step(dt)]
        self._tail_pub.publish(tail_msg)

    def publish_stop(self) -> None:
        self._pub.publish(Twist())


def _pump(node: KeyboardTeleop, fd: int, carry: bytes) -> bytes:
    """Drain the terminal once and apply whatever keys arrived.

    Reads the raw descriptor rather than ``sys.stdin``: see the note in
    :mod:`robot_cat_teleop.keys` about buffering swallowing escape sequences.

    Returns the trailing partial escape sequence, to be passed back in on the
    next call.
    """
    if not select.select([fd], [], [], 0.0)[0]:
        return carry

    try:
        chunk = os.read(fd, 4096)
    except (BlockingIOError, InterruptedError):
        return carry
    if not chunk:
        return carry

    events, leftover = decode_keys(carry + chunk)
    for event in events:
        if event == QUIT:
            node.request_quit()
        elif event == TAIL_STEP:
            node.step_tail()
        elif event == CAMERA_CYCLE:
            node.cycle_camera()
        elif event == MEOW:
            node.meow()
        else:
            node.note_key(event)
    return leftover


def main(args: list[str] | None = None) -> None:
    if not sys.stdin.isatty():
        print(
            "keyboard_teleop needs an interactive terminal (stdin is not a tty).\n"
            "Run it directly in a terminal, not from a launch file.",
            file=sys.stderr,
        )
        return

    rclpy.init(args=args)
    node = KeyboardTeleop()

    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)

    def restore() -> None:
        termios.tcsetattr(fd, termios.TCSADRAIN, settings)

    # Belt and braces: a crash between here and the finally block would
    # otherwise leave the shell in raw mode with no echo.
    atexit.register(restore)

    print(HELP)
    try:
        tty.setcbreak(fd)
        carry = b""
        while rclpy.ok() and not node.quit_requested:
            carry = _pump(node, fd, carry)
            rclpy.spin_once(node, timeout_sec=0.01)
    except KeyboardInterrupt:
        pass
    finally:
        restore()
        atexit.unregister(restore)
        try:
            node.publish_stop()   # do not leave the cat walking
        except Exception:
            pass
        node.shutdown_camera()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        print("\nteleop stopped, cat halted.")


if __name__ == "__main__":
    main()
