"""ROS 2 node: turn ``/cmd_vel`` into twelve joint position commands.

Subscribes to ``geometry_msgs/Twist`` on ``/cmd_vel`` and publishes a
``std_msgs/Float64MultiArray`` to ``/leg_position_controller/commands`` at a
fixed rate, packed in :data:`~robot_cat_gait.gait.JOINT_ORDER`.

All gait tunables are ROS parameters, so the cat can be retuned live with
``ros2 param set`` instead of a rebuild.
"""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import Empty, Float64MultiArray

from .gait import JOINT_ORDER, GaitGenerator, GaitParams
from .leg_ik import LegGeometry
from .lie_down import LieDownParams, LieDownState
from .stretch import StretchParams, StretchState


class GaitController(Node):
    def __init__(self) -> None:
        super().__init__("gait_controller")

        # --- geometry: must match robot_cat_description/urdf/cat.urdf.xacro ---
        self.declare_parameter("hip_offset", 0.035)
        self.declare_parameter("thigh_length", 0.09)
        self.declare_parameter("calf_length", 0.09)

        # --- gait tunables ---
        self.declare_parameter("cycle_time", 0.5)
        self.declare_parameter("duty_factor", 0.65)
        self.declare_parameter("stance_height", 0.13)
        self.declare_parameter("stance_width", 0.02)
        self.declare_parameter("swing_height", 0.035)
        self.declare_parameter("max_stride", 0.08)
        self.declare_parameter("command_tau", 0.15)
        self.declare_parameter("knee_sign", -1.0)

        # --- node behaviour ---
        self.declare_parameter("publish_rate", 100.0)
        self.declare_parameter("cmd_timeout", 0.5)
        # 0.0 means "use whatever the gait geometry can actually deliver".
        self.declare_parameter("max_linear_speed", 0.0)
        self.declare_parameter("max_angular_speed", 0.0)
        self.declare_parameter("command_topic", "/leg_position_controller/commands")
        self.declare_parameter("stretch_topic", "/stretch")

        # --- stretch shape and timing - see robot_cat_gait.stretch ---
        self.declare_parameter("stretch_reach", 0.055)
        self.declare_parameter("stretch_chest_drop", 0.048)
        self.declare_parameter("stretch_rear_shift", 0.022)
        self.declare_parameter("stretch_rear_rise", 0.012)
        self.declare_parameter("stretch_rise_time", 0.85)
        self.declare_parameter("stretch_hold_time", 0.90)
        self.declare_parameter("stretch_fall_time", 1.00)
        self.declare_parameter("lie_down_topic", "/lie_down")
        self.declare_parameter("lie_down_stance_height", 0.045)
        self.declare_parameter("lie_down_tau", 0.6)

        geom = LegGeometry(
            hip_offset=self._f("hip_offset"),
            thigh_length=self._f("thigh_length"),
            calf_length=self._f("calf_length"),
        )
        params = GaitParams(
            cycle_time=self._f("cycle_time"),
            duty_factor=self._f("duty_factor"),
            stance_height=self._f("stance_height"),
            stance_width=self._f("stance_width"),
            swing_height=self._f("swing_height"),
            max_stride=self._f("max_stride"),
            command_tau=self._f("command_tau"),
            knee_sign=self._f("knee_sign"),
        )
        self._gait = GaitGenerator(geom, params)
        self._stretch_params = StretchParams(
            reach=self._f("stretch_reach"),
            chest_drop=self._f("stretch_chest_drop"),
            rear_shift=self._f("stretch_rear_shift"),
            rear_rise=self._f("stretch_rear_rise"),
            rise_time=self._f("stretch_rise_time"),
            hold_time=self._f("stretch_hold_time"),
            fall_time=self._f("stretch_fall_time"),
        )
        self._stretch = StretchState(self._stretch_params)
        self._lie_down_params = LieDownParams(
            down_stance_height=self._f("lie_down_stance_height"),
            tau=self._f("lie_down_tau"),
        )
        self._lie_down = LieDownState(self._lie_down_params)

        # Clamp commands to what the gait can physically produce. A leg covers
        # at most one max_stride per cycle, so accepting a higher speed would
        # just silently saturate and make /cmd_vel a lie.
        geometric_v = params.max_speed
        geometric_w = params.max_yaw_rate(geom.turn_radius)
        requested_v = self._f("max_linear_speed")
        requested_w = self._f("max_angular_speed")
        self._max_v = min(requested_v, geometric_v) if requested_v > 0.0 else geometric_v
        self._max_w = min(requested_w, geometric_w) if requested_w > 0.0 else geometric_w
        self._cmd_timeout = self._f("cmd_timeout")
        rate = self._f("publish_rate")

        self._vx = 0.0
        self._wz = 0.0
        self._last_cmd = self.get_clock().now()
        self._last_tick = self.get_clock().now()
        self._warned_stale = False

        # Commands are volatile+reliable: a late joiner should not be handed a
        # stale walk command from before it subscribed.
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._pub = self.create_publisher(
            Float64MultiArray, self.get_parameter("command_topic").value, qos
        )
        self._sub = self.create_subscription(Twist, "/cmd_vel", self._on_cmd_vel, 10)
        self._stretch_sub = self.create_subscription(
            Empty, self.get_parameter("stretch_topic").value, self._on_stretch, 10
        )
        self._lie_down_sub = self.create_subscription(
            Empty, self.get_parameter("lie_down_topic").value, self._on_lie_down, 10
        )
        self._timer = self.create_timer(1.0 / rate, self._tick)

        self.get_logger().info(
            f"gait_controller up: {rate:.0f} Hz, cycle {params.cycle_time:.2f} s, "
            f"duty {params.duty_factor:.2f}, stance {params.stance_height:.3f} m, "
            f"limits {self._max_v:.2f} m/s and {self._max_w:.2f} rad/s, "
            f"driving {len(JOINT_ORDER)} joints"
        )

    def _f(self, name: str) -> float:
        return float(self.get_parameter(name).value)

    def _on_stretch(self, _msg: Empty) -> None:
        if self._lie_down.down or self._lie_down.amount > 0.01:
            self.get_logger().info("cannot stretch while lying down")
            return
        if self._stretch.trigger():
            self.get_logger().info(
                f"stretching for {self._stretch_params.duration:.1f}s"
            )

    def _on_lie_down(self, _msg: Empty) -> None:
        # Lying down and stretching can't coexist; a toggle to lie down wins
        # outright and cuts the stretch short rather than queuing behind it.
        self._stretch.cancel()
        down = self._lie_down.toggle()
        self.get_logger().info("lying down" if down else "standing up")

    def _on_cmd_vel(self, msg: Twist) -> None:
        self._vx = max(-self._max_v, min(self._max_v, msg.linear.x))
        self._wz = max(-self._max_w, min(self._max_w, msg.angular.z))
        self._last_cmd = self.get_clock().now()
        self._warned_stale = False

    def _tick(self) -> None:
        now = self.get_clock().now()
        dt = (now - self._last_tick).nanoseconds * 1e-9
        self._last_tick = now
        # Guard against a zero or absurd dt on the first tick or after a jump
        # in simulation time (e.g. the user resets the world).
        if dt <= 0.0 or dt > 0.5:
            dt = 1.0 / self._f("publish_rate")

        # Watchdog: if teleop dies or the terminal is closed, stop walking
        # rather than running off with the last command forever.
        age = (now - self._last_cmd).nanoseconds * 1e-9
        if age > self._cmd_timeout:
            if not self._warned_stale and (self._vx or self._wz):
                self.get_logger().warn(
                    f"no /cmd_vel for {age:.1f}s - holding stance"
                )
                self._warned_stale = True
            vx, wz = 0.0, 0.0
        else:
            vx, wz = self._vx, self._wz

        msg = Float64MultiArray()
        lie_amount = self._lie_down.step(dt)
        if self._lie_down.down or lie_amount > 1e-4:
            # A lying cat is neither walking nor stretching. Reset the gait
            # phase so standing back up resumes from a planted stance rather
            # than mid-swing, same reasoning as the stretch branch below.
            self._gait.reset()
            msg.data = self._gait.lie_pose(lie_amount, self._lie_down_params)
        elif self._stretch.active:
            # A stretching cat is not a walking cat. Suppress the gait for the
            # duration and reset its phase, so releasing the stretch resumes
            # from a planted stance rather than mid-swing.
            amount = self._stretch.step(dt)
            self._gait.reset()
            msg.data = self._gait.stretch_pose(amount, self._stretch_params)
        else:
            msg.data = self._gait.step(dt, vx, wz)
        self._pub.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = GaitController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
