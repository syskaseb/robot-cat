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
    knee_sign_for,
)

# Joint limits declared in robot_cat_description/urdf/cat.urdf.xacro. The calf
# range is mirrored for rear legs (see leg.xacro's knee_sign comment) - a real
# hind knee bends the opposite way from a front elbow, so front and rear
# calves cannot share one range.
HIP_LIMITS = (-0.80, 0.80)
THIGH_LIMITS = (-1.45, 2.60)
CALF_LIMITS_FRONT = (-2.70, -0.10)
CALF_LIMITS_REAR = (0.10, 2.70)


def _limits_for(leg: str, joint_index: int) -> tuple[float, float]:
    if joint_index == 0:
        return HIP_LIMITS
    if joint_index == 1:
        return THIGH_LIMITS
    return CALF_LIMITS_FRONT if X_SIGN[leg] > 0.0 else CALF_LIMITS_REAR


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
            leg = LEGS[idx // 3]
            low, high = _limits_for(leg, idx % 3)
            assert low <= value <= high, f"{JOINT_ORDER[idx]}={value:.3f} outside {low, high}"


def test_knee_sign_mirrors_between_front_and_rear():
    """The whole fix in one assertion: a hind knee must bend the opposite
    way from a front elbow, not copy it."""
    assert knee_sign_for("fl", front_knee_sign=-1.0) == -1.0
    assert knee_sign_for("fr", front_knee_sign=-1.0) == -1.0
    assert knee_sign_for("rl", front_knee_sign=-1.0) == 1.0
    assert knee_sign_for("rr", front_knee_sign=-1.0) == 1.0


def test_knee_sign_still_mirrors_if_the_front_convention_flips():
    """Derived from front_knee_sign, not hardcoded, so retuning the front
    branch cannot silently leave the rear one pointing the wrong way."""
    assert knee_sign_for("fl", front_knee_sign=1.0) == 1.0
    assert knee_sign_for("rl", front_knee_sign=1.0) == -1.0


def test_standing_rear_knee_is_ahead_of_the_hip():
    """Read the anatomy back through forward kinematics rather than raw
    joint angles, which would just re-encode the fix by hand."""
    from robot_cat_gait.leg_ik import leg_fk

    gait = GaitGenerator()
    targets = dict(zip(JOINT_ORDER, gait.stand()))
    knee_x = -gait.geom.thigh_length * math.sin(targets["rl_thigh_joint"])
    assert knee_x > 0, "hind knee must point toward the head, not the tail"


def test_standing_front_elbow_is_still_behind_the_hip():
    """The fix must not have touched the front legs, which were already
    anatomically correct."""
    gait = GaitGenerator()
    targets = dict(zip(JOINT_ORDER, gait.stand()))
    knee_x = -gait.geom.thigh_length * math.sin(targets["fl_thigh_joint"])
    assert knee_x < 0, "front elbow must point toward the tail"


def test_front_and_rear_feet_land_in_the_same_place_despite_the_mirror():
    """The whole reason this was a safe change: knee_sign only selects which
    of the two IK branches reaches a target, so the foot's own path through
    space must be identical to the pre-fix, uniform-knee-sign gait."""
    from robot_cat_gait.leg_ik import leg_fk

    gait = GaitGenerator()
    targets = dict(zip(JOINT_ORDER, gait.stand()))
    front = leg_fk(
        targets["fl_hip_joint"], targets["fl_thigh_joint"], targets["fl_calf_joint"],
        gait.geom, y_sign=1.0,
    )
    rear = leg_fk(
        targets["rl_hip_joint"], targets["rl_thigh_joint"], targets["rl_calf_joint"],
        gait.geom, y_sign=1.0,
    )
    assert front[0] == pytest.approx(rear[0], abs=1e-9), "same x offset from hip"
    assert front[2] == pytest.approx(rear[2], abs=1e-9), "same stance height"


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
