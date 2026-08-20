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

from .keys import QUIT, STOP, decode_keys

HELP = """
robot cat teleop
----------------
  up / down     walk forwards / backwards
  left / right  turn left / right
  space         stop
  q or Ctrl-C   quit

Hold a key to keep moving. Keep this terminal focused.
"""




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

        self._lin = float(self.get_parameter("linear_speed").value)
        self._ang = float(self.get_parameter("angular_speed").value)
        self._hold = float(self.get_parameter("key_hold_timeout").value)
        rate = float(self.get_parameter("publish_rate").value)

        self._pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self._pressed: dict[str, float] = {}
        self._quit = False
        self._timer = self.create_timer(1.0 / rate, self._tick)

    def note_key(self, key: str) -> None:
        self._pressed[key] = self._now()

    def stop_all(self) -> None:
        self._pressed.clear()

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
        elif event == STOP:
            node.stop_all()
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
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        print("\nteleop stopped, cat halted.")


if __name__ == "__main__":
    main()
