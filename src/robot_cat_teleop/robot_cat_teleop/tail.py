"""Stepped tail motion for the space bar. Pure maths - no ROS.

Space does not set an angle, it nudges the tail one step along its current
sweep direction, and the direction reverses on reaching either end. Repeated
presses therefore walk the tail down, back up, and down again without any
second key, which suits a tail better than hold-to-move: a cat's tail sets a
pose and holds it, it does not track a control continuously.

The rest pose in ``cat.urdf.xacro`` already carries the tail up, so the sweep
starts heading **down** from there - the first press lowers.

Angles are the ``tail_joint`` position, relative to that rest pose:

====================  =========================================
angle                 pose
====================  =========================================
:attr:`max_angle`     straight up, the alert/greeting tail
0.0                   rest, up and back at roughly 40 degrees
:attr:`min_angle`     down and back, the relaxed droop
====================  =========================================

Unlike the head, this filters *position* rather than velocity: the target is
already a discrete step, so the exponential approach gives the quick snap and
slow settle of a flick, with no ease-in to soften it.
"""

from __future__ import annotations

from dataclasses import dataclass

from .smoothing import ease


@dataclass
class TailParams:
    """Tunables for the tail sweep.

    The limits are the *reachable* ends of the sweep, not the URDF joint
    limits - keep them inside those, or the controller will fight the stop.
    """

    min_angle: float = -1.2
    max_angle: float = 0.9
    step: float = 0.3
    """Radians per press. The full sweep is (max - min) / step presses, so
    the default is seven presses end to end - enough to place the tail
    deliberately, few enough that a reversal never feels far away."""
    tau: float = 0.10
    """Seconds for the tail to close ~63% of the gap to its target."""


class TailState:
    """Turns space-bar presses into a smoothed ``tail_joint`` angle."""

    def __init__(self, params: TailParams | None = None) -> None:
        self.params = params or TailParams()
        self.target = 0.0
        self.angle = 0.0
        # Rest is tail-up, so the opening move is downwards.
        self._direction = -1.0

    @property
    def direction(self) -> float:
        """+1 if the next press raises the tail, -1 if it lowers it."""
        return self._direction

    def press(self) -> float:
        """Advance one step, reversing at either end. Returns the new target.

        The press that *lands* on a limit stops there; the one after it goes
        back the other way.
        """
        p = self.params
        nxt = self.target + self._direction * p.step

        if nxt >= p.max_angle:
            nxt = p.max_angle
            self._direction = -1.0
        elif nxt <= p.min_angle:
            nxt = p.min_angle
            self._direction = 1.0

        self.target = nxt
        return self.target

    def step(self, dt: float) -> float:
        """Ease toward the current target. Returns the angle to publish."""
        self.angle = ease(self.angle, self.target, dt, self.params.tau)
        return self.angle
