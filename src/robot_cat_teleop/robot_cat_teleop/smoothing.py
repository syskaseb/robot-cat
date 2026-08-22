"""Easing helpers shared by the head and tail motion. Pure maths, no ROS.

Both cosmetic joints move through a first-order low-pass filter rather than
jumping to their setpoint - that ease is the whole difference between "servo
snapped to an angle" and "animal moved". They filter different quantities
(the head filters velocity, the tail filters position), so the helper lives
here rather than in either one.
"""

from __future__ import annotations


def ease(current: float, target: float, dt: float, tau: float) -> float:
    """One step of a first-order low-pass filter toward `target`.

    ``dt / tau`` is the fraction of the remaining gap closed this step,
    clamped to 1 so a large `dt` (the first tick, or a sim-time jump) cannot
    overshoot into oscillation.
    """
    alpha = 1.0 if tau <= 0.0 else min(1.0, dt / tau)
    return current + (target - current) * alpha


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))
