"""The loaf: lying down with all four knees folded under the body.

Pure maths, no ROS - same rationale as :mod:`robot_cat_gait.gait` and
:mod:`robot_cat_gait.stretch`.

Unlike the stretch, this is a **toggle** with no timeline of its own: press
once to lie down, press again to stand back up, and the transition reverses
cleanly from wherever it currently is if the second press lands mid-motion.
That is why it is driven by an eased approach to a 0/1 target rather than a
fixed rise/hold/fall schedule - a schedule has no sensible "reverse" partway
through.

The pose itself is just the normal standing stance with every leg's
hip-to-foot distance shortened to :attr:`LieDownParams.down_stance_height`,
symmetric across all four legs. That symmetry is what makes it a loaf and not
a stretch: the stretch pushes front and rear in opposite directions, this
pulls all four legs in together.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LieDownParams:
    """Shape and timing of lying down."""

    down_stance_height: float = 0.045
    """Hip-to-foot distance while lying, in metres, vs. 0.13 standing.

    Chosen close to the leg's mechanical limit rather than at it: at 0.035 the
    calf joint clips its -2.70 rad stop entirely (leg_ik saturates and the
    knee angle silently stops tracking the target), and 0.04 leaves only 0.007
    rad of headroom. 0.045 leaves a real margin while still reading as a full
    fold, not a crouch.
    """

    tau: float = 0.6
    """Seconds to close ~63% of the gap on the way down *or* up.

    Slower than the tail's 0.10 s on purpose: lying down is a full-body
    weight shift, and snapping it at tail speed reads as falling over rather
    than settling.
    """


class LieDownState:
    """Turns presses of one key into a smoothed lying amount, 0 (standing)
    to 1 (fully down)."""

    def __init__(self, params: LieDownParams | None = None) -> None:
        self.params = params or LieDownParams()
        self.target = 0.0
        self.amount = 0.0

    @property
    def down(self) -> bool:
        """Which way the *next* toggle will go is `not down`; this reports
        which state is currently targeted, not whether the motion has
        finished settling."""
        return self.target > 0.5

    def toggle(self) -> bool:
        """Flip the target. Returns the new target state (True = lying)."""
        self.target = 0.0 if self.target > 0.5 else 1.0
        return self.down

    def force_stand(self) -> None:
        """Snap the target to standing without waiting for a toggle.

        For states that should never coexist with lying down - a stretch
        starting, say - rather than leaving the caller to reason about
        toggle() twice cancelling out.
        """
        self.target = 0.0

    def step(self, dt: float) -> float:
        """Ease toward the current target. Returns the amount to pose with."""
        tau = max(self.params.tau, 1e-6)
        alpha = min(1.0, dt / tau)
        self.amount += (self.target - self.amount) * alpha
        return self.amount
