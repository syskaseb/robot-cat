"""Smooth head motion for W/A/S/D. Pure maths - no ROS - so it can be unit
tested the same way as the gait.

A real cat does not snap its head to a new angle; it accelerates into the
motion and eases out of it, and it stops holding a limit rather than pushing
against it. :class:`HeadState` reproduces that with a single first-order
velocity filter: the *target* velocity is either zero or the max rate
(depending on which key, if any, is held), and the *actual* velocity chases
that target with time constant :attr:`HeadParams.velocity_tau`. Position is
then the integral of velocity, clamped to the joint limits.

``tau`` is the only "feel" knob: small values snap, large values feel heavy
and sluggish. 0.12 s reads as an alert, unhurried look-around.
"""

from __future__ import annotations

from dataclasses import dataclass

from .smoothing import clamp, ease


@dataclass
class HeadParams:
    """Tunables for head motion. Ranges are deliberately modest: this is a
    small, stylised head, and a wide swing reads as unnatural rather than
    alert."""

    pan_lower: float = -0.6
    pan_upper: float = 0.6
    #: Cats look up (curiosity, tracking) more than they look down.
    tilt_lower: float = -0.3
    tilt_upper: float = 0.5
    max_rate: float = 1.4
    """rad/s at full speed, once the velocity filter has caught up."""
    velocity_tau: float = 0.12
    """Seconds for velocity to close ~63% of the gap to its target - the
    ease-in/ease-out that makes the motion read as alive rather than
    servo-snapped."""


class HeadState:
    """Integrates held-key direction into a smoothed (pan, tilt) pose.

    `pan_dir` / `tilt_dir` are direction inputs in [-1, 1] (in practice -1,
    0 or 1 - one key held, the opposite key held, or neither); `step` returns
    the joint targets to publish this tick.
    """

    def __init__(self, params: HeadParams | None = None) -> None:
        self.params = params or HeadParams()
        self.pan = 0.0
        self.tilt = 0.0
        self._pan_vel = 0.0
        self._tilt_vel = 0.0

    def step(self, dt: float, pan_dir: float, tilt_dir: float) -> tuple[float, float]:
        p = self.params
        pan_dir = clamp(pan_dir, -1.0, 1.0)
        tilt_dir = clamp(tilt_dir, -1.0, 1.0)

        self._pan_vel = ease(self._pan_vel, pan_dir * p.max_rate, dt, p.velocity_tau)
        self._tilt_vel = ease(self._tilt_vel, tilt_dir * p.max_rate, dt, p.velocity_tau)

        self.pan = clamp(self.pan + self._pan_vel * dt, p.pan_lower, p.pan_upper)
        self.tilt = clamp(self.tilt + self._tilt_vel * dt, p.tilt_lower, p.tilt_upper)

        # Stop pushing once a limit is hit, rather than holding velocity
        # against it - otherwise releasing the key produces a sudden jerk
        # back off the stop as the pent-up velocity finally decays.
        if self.pan in (p.pan_lower, p.pan_upper):
            self._pan_vel = 0.0
        if self.tilt in (p.tilt_lower, p.tilt_upper):
            self._tilt_vel = 0.0

        return self.pan, self.tilt
