"""Trot gait generation for the robot cat.

Pure maths - no ROS imports - so the gait can be unit tested and tuned without
launching a simulator.

The gait is a **trot**: diagonal leg pairs move together and the two diagonals
are half a cycle out of phase, so exactly two feet are on the ground at any
moment. It is the natural gait for a cat at moderate speed and the easiest to
keep statically sane on a simple robot.

Each foot follows a closed loop in the hip frame:

* **stance** - foot is planted; it tracks backwards through the body, pushing
  the cat forwards.
* **swing** - foot lifts on a sine arc and returns to the front.

Turning is differential, exactly like a skid-steer base: the legs on the inside
of the turn take shorter strides than the ones on the outside.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .leg_ik import LegGeometry, leg_ik
from .lie_down import LieDownParams
from .stretch import StretchParams, stretch_offsets

#: Leg names, and the order every 12-element joint vector uses. This is the
#: contract shared with robot_cat_description/config/controllers.yaml.
LEGS: tuple[str, ...] = ("fl", "fr", "rl", "rr")

#: Flat joint ordering: three joints per leg, legs in :data:`LEGS` order.
JOINT_ORDER: tuple[str, ...] = tuple(
    f"{leg}_{joint}_joint" for leg in LEGS for joint in ("hip", "thigh", "calf")
)

#: Trot: fl+rr form one diagonal, fr+rl the other, half a cycle apart.
PHASE_OFFSET: dict[str, float] = {"fl": 0.0, "rr": 0.0, "fr": 0.5, "rl": 0.5}

#: +1 for left legs, -1 for right legs.
Y_SIGN: dict[str, float] = {"fl": 1.0, "rl": 1.0, "fr": -1.0, "rr": -1.0}

#: +1 for front legs, -1 for rear legs.
X_SIGN: dict[str, float] = {"fl": 1.0, "fr": 1.0, "rl": -1.0, "rr": -1.0}


@dataclass
class GaitParams:
    """Tunables for the trot. The defaults are deliberately conservative -
    short, slow strides and a low stance - because legged contact goes unstable
    long before it looks impressive."""

    cycle_time: float = 0.3
    """Seconds for one full gait cycle (both diagonals step once).

    On the original 0.09 m legs, shortening this below 0.5 measurably worsened
    heading drift (24 deg vs 2 deg over 10 s) - the feet got less time to
    settle before the next swap - and 0.5 was the documented sweet spot for a
    long time. The 0.11 m legs changed the trade: re-measured together with
    ``max_stride`` (see the table there), 0.3 now walks at 0.58-0.64 m/s with
    the same ~1 deg/m of heading drift the old default had and *less* body
    roll. The old caution stands if you shorten further - 0.3 is measured,
    below it is not."""

    duty_factor: float = 0.65
    """Fraction of the cycle each foot spends on the ground.

    0.5 is a textbook trot - the diagonals swap instantaneously and the body is
    briefly unsupported. Above 0.5 a double-support phase appears where all four
    feet are down, which is what actually keeps the cat pointing where you aimed
    it. Measured over a 10 s straight-line walk at 0.18 m/s in Gazebo:

    ==========  ==============  =========
    duty        lateral drift   yaw drift
    ==========  ==============  =========
    0.50        0.84 m          26 deg
    **0.65**    **0.17 m**      **2.2 deg**
    0.75        0.17 m          11.8 deg
    ==========  ==============  =========

    0.65 is the sweet spot: enough double support to stay straight, without
    shortening the push-off so much that the cat crawls."""

    stance_height: float = 0.16
    """Hip-to-foot-centre distance when standing, in metres. Ground contact is
    ``foot_radius`` below this.

    Raised 0.13 -> 0.16 alongside the 0.09 -> 0.11 leg segments, to stand the
    cat at roughly its own trunk length - see the comment on ``thigh_length``
    in cat.urdf.xacro. Both moved together on purpose: the ratio that matters
    to the gait is how far the knee is bent, and at 0.16 over a 0.22 m leg
    that is the same 73% of full reach the shorter leg held at 0.13. Raising
    this alone would have straightened the knee to 91% and left the leg with
    no room to swing."""

    stance_width: float = 0.02
    """Extra lateral splay of the feet beyond the hips, in metres.

    At 0 every foot sits directly under its own hip roll joint. That geometry
    is degenerate: ``leg_ik`` solves the roll joint to exactly zero for every
    pose in the gait, whatever the foot is doing, so four of the twelve motors
    never move at all and the only thing resisting body roll is the width of
    the hips themselves. A trot spends most of its cycle balanced on a single
    diagonal pair, which is a narrow base to roll about, and the cat visibly
    wallows.

    Splaying the feet outward fixes both halves of that. Measured in
    ``cat_world`` walking straight at 0.15 m/s, sampling body roll over ~20 s
    of sim time, repeated runs where shown:

    ==========  =====================  ===============
    width       roll peak-to-peak      forward speed
    ==========  =====================  ===============
    0.000       7.7 / 8.2 / 10.7 deg   0.095 m/s
    0.010       3.2 deg                -
    **0.020**   **0.9 - 3.8 deg**      **0.17 m/s**
    0.028       2.5 deg                -
    0.035       2.2 deg                -
    ==========  =====================  ===============

    Anything from 0.01 up lands in the same 2-4 deg band - the spread between
    those rows is run-to-run noise, not a real optimum, so 0.02 is chosen as
    the middle of the working range rather than a tuned minimum. What is well
    outside the noise is the step down from 0: the bands do not overlap.

    The speed roughly doubling is a side effect worth knowing about. The
    wallowing at width 0 was costing paw grip, so the cat slipped instead of
    pushing; a stable body converts more of the same stride into travel.

    Costs reach: holding ``stance_height`` at a wider offset makes the leg
    stretch further, so this trades workspace margin for roll stiffness. At
    0.02 the roll joint holds about 11 deg and sweeps a further 2.7 deg per
    stride, well inside the +/-0.80 rad the joint allows."""

    swing_height: float = 0.035
    """Peak foot lift during swing, in metres."""

    max_stride: float = 0.16
    """Cap on stride length, in metres. Prevents the IK from being asked for
    targets outside the leg's workspace.

    Retuned with ``cycle_time`` when the legs grew to 0.11 m. Measured in
    cat_world, commanded well above the cap so the cap binds, one run per
    cell unless noted - and with **no teleop running**: its idle zeros on
    /cmd_vel interleave with the test command and corrupt every number.

    ==========  ==========  ==============  =============
    stride      cycle       achieved        notes
    ==========  ==========  ==============  =============
    0.08        0.5         0.168 m/s       old default
    0.16        0.5         0.090 m/s       slower! slips
    0.20        0.5         0.034 m/s       leg locked straight
    0.12        0.3         0.19-0.35 m/s
    **0.16**    **0.3**     **0.58-0.64**   drift ~0.9 deg/m, roll 1.6 deg
    ==========  ==========  ==============  =============

    The lesson in the middle rows: a longer stride at the old tempo is
    *slower*, because near the 0.151 m excursion limit the leg is almost
    straight and shears instead of pushing. The speed lives in the
    stride-times-tempo product, not in stride alone. 0.16 does saturate the
    IK briefly at the stride ends; measurement says that costs nothing at
    0.3 s, but treat stride and cycle as a pair when retuning."""

    command_tau: float = 0.15
    """Time constant of the first-order low-pass on incoming velocity commands.
    Smooths starts and stops so the cat does not lurch."""

    stride_deadband: float = 0.002
    """Below this smoothed stride magnitude the gait freezes and the cat simply
    stands, instead of marching in place."""

    knee_sign: float = -1.0
    """IK branch selector, forwarded to :func:`~robot_cat_gait.leg_ik.leg_ik`."""

    @property
    def max_speed(self) -> float:
        """Fastest forward speed the gait can actually produce, in m/s.

        A leg covers at most ``max_stride`` per cycle, so the body cannot
        advance faster than one stride per ``cycle_time``. Commanding more than
        this does nothing - the stride cap simply saturates - so the node clamps
        to it rather than pretending to accept a higher speed.
        """
        return self.max_stride / self.cycle_time

    def max_yaw_rate(self, turn_radius: float) -> float:
        """Fastest yaw rate the gait can produce, in rad/s.

        Same argument as :attr:`max_speed`, but the relevant distance is the arc
        each foot sweeps, at ``turn_radius`` from the body centre.
        """
        return self.max_stride / (self.cycle_time * max(turn_radius, 1e-9))


def foot_offset(
    phase: float,
    stride_x: float,
    stride_y: float,
    params: GaitParams,
    swing_scale: float = 1.0,
) -> tuple[float, float, float]:
    """Foot displacement from its neutral position, for one leg.

    Args:
        phase: Position in this leg's own cycle, in ``[0, 1)``.
        stride_x: Forward component of this leg's stride, in metres. Negative
            when walking backwards.
        stride_y: Lateral component, in metres. Non-zero only when turning -
            a foot on a turning body traces an arc, not a straight line.
        params: Gait tunables.
        swing_scale: Fraction of :attr:`GaitParams.swing_height` to lift. The
            generator ties this to stride length so that the whole gait scales
            continuously from standing still to a full trot - a crawling cat
            should shuffle, not high-step.

    Returns:
        ``(dx, dy, dz)`` in metres: forward, lateral and vertical offsets.
    """
    duty = params.duty_factor

    if phase < duty:
        # Stance: track backwards from +stride/2 to -stride/2, foot on ground.
        s = phase / duty if duty > 0.0 else 0.0
        along = 0.5 - s
        return stride_x * along, stride_y * along, 0.0

    # Swing: return from -stride/2 to +stride/2, lifting on a sine arc.
    s = (phase - duty) / (1.0 - duty) if duty < 1.0 else 0.0
    along = s - 0.5
    lift = params.swing_height * swing_scale * math.sin(math.pi * s)
    return stride_x * along, stride_y * along, lift


def is_stance(phase: float, params: GaitParams) -> bool:
    """Whether a leg at ``phase`` is on the ground."""
    return phase < params.duty_factor


class GaitGenerator:
    """Stateful trot generator.

    Holds the gait phase and the smoothed velocity command between updates.
    Call :meth:`step` at a fixed rate.
    """

    def __init__(
        self,
        geom: LegGeometry | None = None,
        params: GaitParams | None = None,
    ) -> None:
        self.geom = geom or LegGeometry()
        self.params = params or GaitParams()
        self._phase = 0.0
        self._vx = 0.0
        self._wz = 0.0

    @property
    def phase(self) -> float:
        return self._phase

    def reset(self) -> None:
        """Return to a standing pose and zero the smoothed command."""
        self._phase = 0.0
        self._vx = 0.0
        self._wz = 0.0

    def _smooth(self, vx_cmd: float, wz_cmd: float, dt: float) -> None:
        # First-order low-pass. alpha -> 1 as dt grows past the time constant.
        tau = max(self.params.command_tau, 1e-6)
        alpha = 1.0 - math.exp(-dt / tau)
        self._vx += alpha * (vx_cmd - self._vx)
        self._wz += alpha * (wz_cmd - self._wz)

    def _strides(self) -> dict[str, tuple[float, float]]:
        """Per-leg stride vector ``(sx, sy)``, in metres.

        A foot on a body that is both translating and rotating traces an arc,
        not a straight line. Its ground velocity is the rigid-body twist
        evaluated at that foot::

            v_foot = v_body + omega x r_foot

        which for planar motion is ``vx - wz*ry`` forwards and ``wz*rx``
        sideways. Driving only the forward component - as a naive differential
        "left legs step shorter" scheme does - forces the stance feet to scrub
        sideways through the turn, and paw friction then fights the very
        rotation being commanded. That is why turning barely worked until the
        lateral term was added.

        The cap is applied by scaling every leg by one common factor, so
        saturating a fast turn slows the cat down without straightening it out.
        """
        p = self.params
        strides: dict[str, tuple[float, float]] = {}
        for leg in LEGS:
            rx = X_SIGN[leg] * self.geom.mount_x
            ry = Y_SIGN[leg] * self.geom.foot_y
            vx = self._vx - self._wz * ry
            vy = self._wz * rx
            strides[leg] = (vx * p.cycle_time, vy * p.cycle_time)

        largest = max(math.hypot(sx, sy) for sx, sy in strides.values())
        if largest > p.max_stride:
            scale = p.max_stride / largest
            strides = {leg: (sx * scale, sy * scale) for leg, (sx, sy) in strides.items()}
        return strides

    def _neutral_y(self, y_sign: float) -> float:
        """Lateral foot position for one leg, in metres from its hip joint.

        Every pose in this class - walking, standing, stretching, lying down -
        measures its lateral offset from here, so that ``stance_width`` widens
        all of them together and ``stretch_pose(0) == stand()`` stays true.
        """
        return y_sign * (self.geom.hip_offset + self.params.stance_width)

    def step(self, dt: float, vx_cmd: float, wz_cmd: float) -> list[float]:
        """Advance the gait by ``dt`` and return the 12 joint targets.

        Args:
            dt: Time since the previous call, in seconds.
            vx_cmd: Commanded forward velocity, m/s.
            wz_cmd: Commanded yaw rate, rad/s (positive turns left).

        Returns:
            Joint angles in radians, ordered as :data:`JOINT_ORDER`.
        """
        self._smooth(vx_cmd, wz_cmd, dt)
        strides = self._strides()

        longest = max(math.hypot(sx, sy) for sx, sy in strides.values())
        moving = longest > self.params.stride_deadband
        if moving:
            self._phase = (self._phase + dt / self.params.cycle_time) % 1.0
        else:
            # Plant all four feet rather than marching on the spot.
            self._phase = 0.0

        targets: list[float] = []
        for leg in LEGS:
            y_sign = Y_SIGN[leg]
            stride_x, stride_y = strides[leg]

            if moving:
                leg_phase = (self._phase + PHASE_OFFSET[leg]) % 1.0
                # Lift in proportion to stride, so starting and stopping ramps
                # the foot arc up and down instead of switching it on.
                swing_scale = min(
                    1.0, math.hypot(stride_x, stride_y) / self.params.max_stride
                )
                dx, dy, dz = foot_offset(
                    leg_phase, stride_x, stride_y, self.params, swing_scale
                )
            else:
                dx, dy, dz = 0.0, 0.0, 0.0

            targets.extend(
                leg_ik(
                    x=dx,
                    y=self._neutral_y(y_sign) + dy,
                    z=-self.params.stance_height + dz,
                    geom=self.geom,
                    y_sign=y_sign,
                    knee_sign=self.params.knee_sign,
                )
            )

        return targets

    def stretch_pose(
        self, amount: float, params: StretchParams | None = None
    ) -> list[float]:
        """Joint targets for the play-bow stretch at ``amount`` (0..1).

        At 0 this is exactly :meth:`stand`, so the caller can hand it a decaying
        amount and let the cat settle back into its stance with no seam.
        """
        params = params or StretchParams()
        targets: list[float] = []
        for leg in LEGS:
            y_sign = Y_SIGN[leg]
            dx, dz = stretch_offsets(amount, X_SIGN[leg] > 0.0, params)
            targets.extend(
                leg_ik(
                    x=dx,
                    y=self._neutral_y(y_sign),
                    z=-self.params.stance_height + dz,
                    geom=self.geom,
                    y_sign=y_sign,
                    knee_sign=self.params.knee_sign,
                )
            )
        return targets

    def lie_pose(self, amount: float, params: LieDownParams | None = None) -> list[float]:
        """Joint targets for the loaf at ``amount`` (0..1).

        At 0 this is exactly :meth:`stand`, for the same reason
        :meth:`stretch_pose` matches it at 0: no seam when the amount decays
        through zero at the end of standing back up.

        All four legs get the same shortened stance height with no x or y
        offset - unlike the stretch, lying down is symmetric front to back.
        """
        params = params or LieDownParams()
        height = self.params.stance_height + amount * (
            params.down_stance_height - self.params.stance_height
        )
        targets: list[float] = []
        for leg in LEGS:
            y_sign = Y_SIGN[leg]
            targets.extend(
                leg_ik(
                    x=0.0,
                    y=self._neutral_y(y_sign),
                    z=-height,
                    geom=self.geom,
                    y_sign=y_sign,
                    knee_sign=self.params.knee_sign,
                )
            )
        return targets

    def stand(self) -> list[float]:
        """Joint targets for the neutral standing pose, ignoring gait phase."""
        targets: list[float] = []
        for leg in LEGS:
            y_sign = Y_SIGN[leg]
            targets.extend(
                leg_ik(
                    x=0.0,
                    y=self._neutral_y(y_sign),
                    z=-self.params.stance_height,
                    geom=self.geom,
                    y_sign=y_sign,
                    knee_sign=self.params.knee_sign,
                )
            )
        return targets
