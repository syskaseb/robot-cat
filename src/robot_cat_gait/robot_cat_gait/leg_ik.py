"""Analytic inverse kinematics for one 3-DOF quadruped leg.

Pure maths - no ROS imports - so it can be unit tested without a simulator.

Leg chain (see robot_cat_description/urdf/leg.xacro, which MUST use the same
numbers as LegGeometry below):

    hip joint   revolute about X (abduction/adduction)
      -> hip link, offset `d` outward along Y
    thigh joint revolute about Y (pitch), thigh length L1 downward
      -> knee
    calf joint  revolute about Y (pitch), calf length L2 downward
      -> foot

All foot targets are expressed in the *hip frame*: origin at the hip joint,
axes aligned with base_link when every joint is at zero (x forward, y left,
z up, per REP-103).

Forward kinematics, for reference::

    x_l = -L1*sin(qt) - L2*sin(qt + qc)
    z_l = -L1*cos(qt) - L2*cos(qt + qc)
    p   = Rx(qh) @ (x_l, d, z_l)
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class LegGeometry:
    """Link lengths of one leg, in metres.

    Keep in sync with the xacro properties in
    robot_cat_description/urdf/cat.urdf.xacro.
    """

    hip_offset: float = 0.025
    """Lateral distance from the hip (roll) joint to the thigh (pitch) joint."""

    thigh_length: float = 0.11
    """L1 - thigh joint to knee joint."""

    calf_length: float = 0.11
    """L2 - knee joint to foot contact point."""

    mount_x: float = 0.11
    """Hip joint offset from the body centre along X (front legs are +)."""

    mount_y: float = 0.055
    """Hip joint offset from the body centre along Y (left legs are +)."""

    @property
    def foot_y(self) -> float:
        """Lateral distance from the body centreline to a neutral foot."""
        return self.mount_y + self.hip_offset

    @property
    def max_reach(self) -> float:
        return self.thigh_length + self.calf_length

    @property
    def turn_radius(self) -> float:
        """Distance from the body centre to a neutral foot, in metres."""
        return math.hypot(self.mount_x, self.foot_y)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def leg_ik(
    x: float,
    y: float,
    z: float,
    geom: LegGeometry,
    y_sign: float,
    knee_sign: float = -1.0,
) -> tuple[float, float, float]:
    """Solve for the joint angles that place the foot at ``(x, y, z)``.

    Args:
        x, y, z: Foot target in the hip frame. ``z`` is normally negative
            (the foot is below the hip).
        geom: Link lengths.
        y_sign: ``+1`` for left legs, ``-1`` for right legs. Selects which way
            the hip offset points.
        knee_sign: Which IK branch to take, i.e. which way the knee bends.
            ``-1`` bends the knee backwards. Flip to ``+1`` for the mirrored
            solution.

    Returns:
        ``(q_hip, q_thigh, q_calf)`` in radians.

    Targets outside the leg's reachable workspace are saturated to the nearest
    reachable pose rather than raising, so a mistuned gait degrades instead of
    crashing the controller.
    """
    d = y_sign * geom.hip_offset
    l1 = geom.thigh_length
    l2 = geom.calf_length

    # --- hip roll -------------------------------------------------------
    # Rotating (d, z_l) about X by q_hip must land on (y, z), so the radius is
    # preserved: y^2 + z^2 == d^2 + z_l^2.
    yz_sq = y * y + z * z
    z_planar = -math.sqrt(max(yz_sq - d * d, 0.0))
    q_hip = math.atan2(z, y) - math.atan2(z_planar, d)
    q_hip = math.atan2(math.sin(q_hip), math.cos(q_hip))  # wrap to [-pi, pi]

    # --- knee + thigh, in the sagittal plane ----------------------------
    # Substituting X = -z_planar, Y = -x turns this into a textbook planar 2R
    # arm, so the standard elbow solution applies.
    reach = math.hypot(x, z_planar)
    cos_knee = (reach * reach - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)
    q_calf = knee_sign * math.acos(_clamp(cos_knee, -1.0, 1.0))

    q_thigh = math.atan2(-x, -z_planar) - math.atan2(
        l2 * math.sin(q_calf), l1 + l2 * math.cos(q_calf)
    )

    return q_hip, q_thigh, q_calf


def leg_fk(
    q_hip: float,
    q_thigh: float,
    q_calf: float,
    geom: LegGeometry,
    y_sign: float,
) -> tuple[float, float, float]:
    """Forward kinematics - the inverse of :func:`leg_ik`, used to verify it."""
    d = y_sign * geom.hip_offset
    l1 = geom.thigh_length
    l2 = geom.calf_length

    x_l = -l1 * math.sin(q_thigh) - l2 * math.sin(q_thigh + q_calf)
    z_l = -l1 * math.cos(q_thigh) - l2 * math.cos(q_thigh + q_calf)

    ch, sh = math.cos(q_hip), math.sin(q_hip)
    return (
        x_l,
        d * ch - z_l * sh,
        d * sh + z_l * ch,
    )
