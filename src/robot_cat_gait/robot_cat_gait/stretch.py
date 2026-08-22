"""The play-bow stretch: front down, rear up, hold, release.

Pure maths, no ROS, so the shape of the movement can be tested and tuned
without a simulator - same rationale as :mod:`robot_cat_gait.gait`.

A stretching cat is not doing one thing, it is doing four at once, and
leaving any of them out makes it read as "crouching" rather than
"stretching":

* the front feet **reach forward**, well ahead of the shoulders;
* the chest **drops** toward the floor, folding the front legs;
* the rear legs **straighten**, pushing the hips up and back;
* and it is **held** - the hold is what separates a stretch from a stumble.

The motion is driven by a single 0..1 amount rather than per-joint keyframes.
Every offset is that amount times its full extent, so the pose is guaranteed
to start and finish exactly at the neutral stance no matter where the timings
are retuned to.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StretchParams:
    """Shape and timing of one stretch."""

    reach: float = 0.055
    """How far forward the front feet slide, in metres."""

    chest_drop: float = 0.048
    """How much the front hip-to-foot distance shortens, in metres. This is
    what lowers the chest; it folds the front legs rather than moving the
    body directly."""

    rear_shift: float = 0.022
    """How far back the rear feet plant, in metres."""

    rear_rise: float = 0.012
    """Extra rear hip-to-foot distance, in metres - the hips lifting."""

    rise_time: float = 0.85
    """Seconds to ease into the pose."""

    hold_time: float = 0.90
    """Seconds held at full stretch. Without this it looks like a stumble."""

    fall_time: float = 1.00
    """Seconds to ease back out. Slower than the way in: cats collapse out of
    a stretch more lazily than they go into it."""

    @property
    def duration(self) -> float:
        return self.rise_time + self.hold_time + self.fall_time


def smoothstep(t: float) -> float:
    """Ease 0..1 with zero velocity at both ends.

    A linear ramp starts and stops with a visible jerk, because the joint
    velocity steps from zero to full instantly.
    """
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def stretch_amount(elapsed: float, params: StretchParams) -> float:
    """How far into the stretch the cat is, 0 (neutral) to 1 (full).

    Args:
        elapsed: Seconds since the stretch began.
        params: Timings to use.

    Returns:
        0.0 before the start and after the end, so the caller can drive this
        straight through :func:`stretch_offsets` without special-casing.
    """
    if elapsed <= 0.0:
        return 0.0
    if elapsed < params.rise_time:
        return smoothstep(elapsed / params.rise_time)
    if elapsed < params.rise_time + params.hold_time:
        return 1.0
    remaining = elapsed - params.rise_time - params.hold_time
    if remaining < params.fall_time:
        return smoothstep(1.0 - remaining / params.fall_time)
    return 0.0


def stretch_offsets(
    amount: float, is_front: bool, params: StretchParams
) -> tuple[float, float]:
    """Foot offset for one leg at a given stretch amount.

    Args:
        amount: 0..1 from :func:`stretch_amount`.
        is_front: Front legs fold and reach; rear legs straighten and shift back.
        params: Extents to use.

    Returns:
        ``(dx, dz)`` in metres, to add to the neutral foot position in the hip
        frame. Positive ``dz`` shortens the hip-to-foot distance.
    """
    if is_front:
        return amount * params.reach, amount * params.chest_drop
    return -amount * params.rear_shift, -amount * params.rear_rise


class StretchState:
    """Tracks one stretch from trigger to finish.

    Retriggering while a stretch is running is ignored rather than restarting
    it: key autorepeat would otherwise pin the cat at the start of the pose
    for as long as the key is held.
    """

    def __init__(self, params: StretchParams | None = None) -> None:
        self.params = params or StretchParams()
        self._elapsed: float | None = None

    @property
    def active(self) -> bool:
        return self._elapsed is not None

    def trigger(self) -> bool:
        """Begin a stretch. Returns False if one is already running."""
        if self._elapsed is not None:
            return False
        self._elapsed = 0.0
        return True

    def cancel(self) -> None:
        self._elapsed = None

    def step(self, dt: float) -> float:
        """Advance time and return the current amount, 0 when not stretching."""
        if self._elapsed is None:
            return 0.0
        self._elapsed += dt
        if self._elapsed >= self.params.duration:
            self._elapsed = None
            return 0.0
        return stretch_amount(self._elapsed, self.params)
