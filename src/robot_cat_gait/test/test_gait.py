"""Gait invariants - the properties that make it a trot rather than a flail."""

import math

import pytest

from robot_cat_gait.gait import (
    JOINT_ORDER,
    LEGS,
    PHASE_OFFSET,
    X_SIGN,
    Y_SIGN,
    GaitGenerator,
    GaitParams,
    foot_offset,
    is_stance,
)

# Joint limits declared in robot_cat_description/urdf/cat.urdf.xacro.
LIMITS = {0: (-0.80, 0.80), 1: (-1.20, 2.60), 2: (-2.70, -0.10)}


def test_joint_order_matches_controller_contract():
    assert len(JOINT_ORDER) == 12
    assert JOINT_ORDER[0] == "fl_hip_joint"
    assert JOINT_ORDER[-1] == "rr_calf_joint"


def _feet_down(phase: float, params: GaitParams) -> int:
    return sum(is_stance((phase + PHASE_OFFSET[leg]) % 1.0, params) for leg in LEGS)


@pytest.mark.parametrize("phase", [i / 200.0 for i in range(200)])
def test_never_fewer_than_two_feet_on_the_ground(phase):
    """The cat must never be airborne or balanced on a single paw."""
    assert _feet_down(phase, GaitParams()) >= 2


@pytest.mark.parametrize("phase", [i / 200.0 for i in range(200)])
def test_pure_trot_at_duty_half_has_exactly_two_feet_down(phase):
    """duty_factor 0.5 is the textbook trot: instantaneous diagonal swap."""
    assert _feet_down(phase, GaitParams(duty_factor=0.5)) == 2


def test_default_duty_gives_a_double_support_phase():
    """The default trades pure-trot elegance for heading stability: above
    duty 0.5 there are stretches with all four feet down, which is what keeps
    the cat walking straight (12x less yaw drift, measured in Gazebo)."""
    params = GaitParams()
    assert params.duty_factor > 0.5
    counts = {_feet_down(i / 500.0, params) for i in range(500)}
    assert 4 in counts, "expected a four-feet-down phase"
    assert min(counts) == 2


def test_diagonal_pairs_move_together():
    assert PHASE_OFFSET["fl"] == PHASE_OFFSET["rr"]
    assert PHASE_OFFSET["fr"] == PHASE_OFFSET["rl"]
    assert PHASE_OFFSET["fl"] != PHASE_OFFSET["fr"]


def test_foot_trajectory_is_a_closed_continuous_loop():
    params = GaitParams()
    pts = [foot_offset(i / 1000.0, 0.06, 0.0, params) for i in range(1000)]
    assert max(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) < 1e-3
    assert math.dist(pts[-1], pts[0]) < 1e-3


def test_turning_foot_trajectory_is_also_closed():
    """A foot on a turning body sweeps an arc; that loop must close too."""
    params = GaitParams()
    pts = [foot_offset(i / 1000.0, 0.04, 0.03, params) for i in range(1000)]
    assert max(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) < 1e-3
    assert math.dist(pts[-1], pts[0]) < 1e-3


def test_foot_stays_on_the_ground_through_stance():
    params = GaitParams()
    for i in range(100):
        phase = i / 100.0 * params.duty_factor
        assert foot_offset(phase, 0.06, 0.0, params)[2] == 0.0


def test_swing_lifts_the_foot():
    params = GaitParams()
    mid_swing = params.duty_factor + (1.0 - params.duty_factor) / 2.0
    assert foot_offset(mid_swing, 0.06, 0.0, params)[2] == pytest.approx(
        params.swing_height
    )


def test_stride_span_matches_commanded_stride():
    params = GaitParams()
    xs = [foot_offset(i / 500.0, 0.06, 0.0, params)[0] for i in range(500)]
    assert max(xs) - min(xs) == pytest.approx(0.06, abs=1e-3)


@pytest.mark.parametrize(
    "vx,wz",
    [(0.0, 0.0), (0.25, 0.0), (-0.25, 0.0), (0.0, 2.5), (0.0, -2.5), (0.2, 1.5)],
)
def test_commands_stay_within_urdf_joint_limits(vx, wz):
    """A gait that commands out-of-limit angles silently saturates in Gazebo
    and walks wrong, so guard the whole envelope here instead."""
    gait = GaitGenerator()
    for _ in range(400):
        targets = gait.step(0.01, vx, wz)
        assert len(targets) == 12
        for idx, value in enumerate(targets):
            low, high = LIMITS[idx % 3]
            assert low <= value <= high, f"{JOINT_ORDER[idx]}={value:.3f} outside {low, high}"


def _hip_angles(params: GaitParams, ticks: int = 200) -> list[float]:
    """Every fl_hip_joint value over a stretch of straight walking."""
    gait = GaitGenerator(params=params)
    seen = []
    for _ in range(ticks):
        seen.append(gait.step(0.005, 0.15, 0.0)[JOINT_ORDER.index("fl_hip_joint")])
    return seen


def test_feet_directly_under_the_hips_leave_the_roll_joints_dead():
    """The degeneracy stance_width exists to break: with the foot in the
    plane of its own hip, the roll solution is zero no matter what the rest
    of the leg does, so four of the twelve motors never move."""
    angles = _hip_angles(GaitParams(stance_width=0.0))
    assert max(angles) == pytest.approx(0.0, abs=1e-12)
    assert min(angles) == pytest.approx(0.0, abs=1e-12)


def test_stance_width_puts_the_hip_roll_joints_to_work():
    """Splaying the feet both holds the hips off zero and makes them sweep -
    the sweep falls out of the swing lift, which only tilts the leg plane
    once the foot is outside it."""
    angles = _hip_angles(GaitParams(stance_width=0.02))
    assert min(angles) > 0.05, "hips must hold a real splay, not hover near zero"
    assert max(angles) - min(angles) > 0.01, "hips must move across the stride"


def test_stance_width_widens_the_feet_without_lowering_the_body():
    """Roll stiffness has to come from a wider base, not from a crouch - if
    this dropped stance height it would be trading one fix for a worse one."""
    from robot_cat_gait.leg_ik import leg_fk

    narrow, wide = (
        GaitGenerator(params=GaitParams(stance_width=w)).stand() for w in (0.0, 0.02)
    )
    i = JOINT_ORDER.index("fl_hip_joint")
    geom = GaitGenerator().geom
    a = leg_fk(*narrow[i : i + 3], geom, y_sign=1.0)
    b = leg_fk(*wide[i : i + 3], geom, y_sign=1.0)
    assert b[1] == pytest.approx(a[1] + 0.02, abs=1e-9), "foot 2 cm further out"
    assert b[2] == pytest.approx(a[2], abs=1e-9), "same height off the hip"


@pytest.mark.parametrize("width", [0.0, 0.01, 0.02, 0.035, 0.05])
def test_stance_width_keeps_every_joint_inside_its_limits(width):
    """Widening costs reach, so the splay has to stay inside the same URDF
    limits the rest of the gait is checked against."""
    gait = GaitGenerator(params=GaitParams(stance_width=width))
    for _ in range(200):
        for idx, value in enumerate(gait.step(0.01, 0.15, 0.4)):
            low, high = LIMITS[idx % 3]
            assert low <= value <= high, f"{JOINT_ORDER[idx]}={value:.3f} at w={width}"


def test_gait_holds_still_when_not_commanded():
    gait = GaitGenerator()
    for _ in range(200):
        gait.step(0.01, 0.0, 0.0)
    assert gait.phase == 0.0
    assert gait.step(0.01, 0.0, 0.0) == pytest.approx(gait.stand())


def test_gait_advances_phase_when_walking():
    gait = GaitGenerator()
    for _ in range(50):
        gait.step(0.01, 0.2, 0.0)
    assert gait.phase > 0.0


def test_saturating_the_stride_scales_every_leg_by_one_factor():
    """Capping each leg independently would flatten a fast arc into a straight
    line: outer legs clip to the cap while inner ones do not, so the difference
    that produces the turn shrinks. Saturating must slow the cat, not
    straighten it."""
    gait = GaitGenerator()
    for _ in range(400):
        gait.step(0.01, 0.25, 2.0)
    strides = gait._strides()

    assert max(math.hypot(*s) for s in strides.values()) <= gait.params.max_stride + 1e-9

    # Every leg keeps its share of the uncapped solution.
    ratios = []
    for leg, (sx, sy) in strides.items():
        rx = X_SIGN[leg] * gait.geom.mount_x
        ry = Y_SIGN[leg] * gait.geom.foot_y
        raw = math.hypot(
            (gait._vx - gait._wz * ry) * gait.params.cycle_time,
            (gait._wz * rx) * gait.params.cycle_time,
        )
        ratios.append(math.hypot(sx, sy) / raw)
    assert max(ratios) == pytest.approx(min(ratios))


def test_turning_makes_inner_legs_take_shorter_strides():
    """Left turn (positive yaw) shortens the forward reach of the left legs."""
    gait = GaitGenerator()
    for _ in range(300):
        gait.step(0.01, 0.2, 1.5)
    strides = gait._strides()
    assert strides["fl"][0] < strides["fr"][0]
    assert strides["rl"][0] < strides["rr"][0]


def test_turning_sweeps_feet_sideways_not_just_fore_aft():
    """The whole point of the 2D stride: on a turn each foot follows the arc
    its body corner traces. Without the lateral term the stance feet scrub
    sideways and friction cancels the turn."""
    gait = GaitGenerator()
    for _ in range(400):
        gait.step(0.01, 0.0, 1.5)
    strides = gait._strides()
    # Pure rotation: front feet swing one way, rear feet the other.
    assert strides["fl"][1] > 0.0 and strides["fr"][1] > 0.0
    assert strides["rl"][1] < 0.0 and strides["rr"][1] < 0.0
    # ...and left/right legs move oppositely fore-aft.
    assert strides["fl"][0] < 0.0 < strides["fr"][0]


def test_pure_spin_produces_no_net_translation():
    """Summing the stride vectors over all four legs must cancel for a pure
    yaw command - otherwise 'turn in place' would creep."""
    gait = GaitGenerator()
    for _ in range(400):
        gait.step(0.01, 0.0, 1.5)
    strides = gait._strides()
    assert sum(sx for sx, _ in strides.values()) == pytest.approx(0.0, abs=1e-12)
    assert sum(sy for _, sy in strides.values()) == pytest.approx(0.0, abs=1e-12)


#: velocity limit on every joint in cat.urdf.xacro, rad/s
URDF_VELOCITY_LIMIT = 20.0


def test_implied_joint_velocity_stays_within_the_urdf_limit():
    """The gait must never ask a joint to move faster than it can.

    A discontinuity here becomes a velocity spike that Gazebo's solver turns
    into the cat kicking itself over, and anything above the URDF limit is
    silently clamped - so the cat would walk differently from the gait the
    maths describes. Bounded at 75% of the limit to leave headroom.
    """
    dt = 0.01
    gait = GaitGenerator()
    previous = gait.step(dt, 0.0, 0.0)
    worst = 0.0
    # stand -> walk -> turn -> reverse -> stop
    profile = [(0.0, 0.0), (0.25, 0.0), (0.2, 1.5), (-0.25, 0.0), (0.0, 0.0)]
    for vx, wz in profile:
        for _ in range(200):
            current = gait.step(dt, vx, wz)
            worst = max(worst, max(abs(a - b) for a, b in zip(current, previous)) / dt)
            previous = current
    assert worst < 0.75 * URDF_VELOCITY_LIMIT, (
        f"peak commanded joint velocity {worst:.1f} rad/s is too close to the "
        f"URDF limit of {URDF_VELOCITY_LIMIT} rad/s"
    )


def test_swing_lift_scales_with_stride():
    """A slow shuffle should not high-step: lift is proportional to stride."""
    params = GaitParams()
    mid_swing = params.duty_factor + (1.0 - params.duty_factor) / 2.0
    full = foot_offset(mid_swing, params.max_stride, 0.0, params, swing_scale=1.0)[2]
    tenth = foot_offset(mid_swing, params.max_stride, 0.0, params, swing_scale=0.1)[2]
    assert tenth == pytest.approx(full * 0.1)


def test_reset_returns_to_stance():
    gait = GaitGenerator()
    for _ in range(100):
        gait.step(0.01, 0.2, 1.0)
    gait.reset()
    assert gait.phase == 0.0
    assert gait.step(0.0, 0.0, 0.0) == pytest.approx(gait.stand())


def test_max_speed_is_one_stride_per_cycle():
    """Commanding faster than this cannot work: the stride cap saturates, so
    the node clamps rather than accepting a speed it will not deliver."""
    params = GaitParams(max_stride=0.08, cycle_time=0.5)
    assert params.max_speed == pytest.approx(0.16)


def test_commanding_above_max_speed_does_not_go_faster():
    at_limit = GaitGenerator()
    over_limit = GaitGenerator()
    for _ in range(400):
        at_limit.step(0.01, at_limit.params.max_speed, 0.0)
        over_limit.step(0.01, at_limit.params.max_speed * 4.0, 0.0)
    a = max(math.hypot(*s) for s in at_limit._strides().values())
    b = max(math.hypot(*s) for s in over_limit._strides().values())
    assert a == pytest.approx(b), "stride saturates, so extra command is wasted"


def test_max_yaw_rate_scales_with_turn_radius():
    params = GaitParams(max_stride=0.08, cycle_time=0.5)
    assert params.max_yaw_rate(0.142) == pytest.approx(0.08 / (0.5 * 0.142))
    # A wider stance means each foot sweeps further per radian, so slower.
    assert params.max_yaw_rate(0.30) < params.max_yaw_rate(0.142)
