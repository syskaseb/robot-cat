"""The stretch's shape over time, and that it starts and ends at the stance.

The pose is generated from a single 0..1 amount, so most of the risk is in
the timing curve: a stretch that does not return exactly to neutral leaves
the cat permanently crouched, and one without a hold reads as a stumble.
"""

import pytest

from robot_cat_gait.gait import JOINT_ORDER, LEGS, X_SIGN, GaitGenerator
from robot_cat_gait.stretch import (
    StretchParams,
    StretchState,
    smoothstep,
    stretch_amount,
    stretch_offsets,
)

P = StretchParams()


# --- easing ---------------------------------------------------------------


def test_smoothstep_spans_zero_to_one():
    assert smoothstep(0.0) == 0.0
    assert smoothstep(1.0) == 1.0


def test_smoothstep_is_flat_at_both_ends():
    """Zero velocity at the ends is the whole point - a linear ramp jerks."""
    assert smoothstep(0.02) < 0.02
    assert smoothstep(0.98) > 0.98


def test_smoothstep_clamps_outside_the_range():
    assert smoothstep(-1.0) == 0.0
    assert smoothstep(5.0) == 1.0


# --- timing curve ---------------------------------------------------------


def test_starts_and_ends_at_neutral():
    # approx at the end only because duration is a sum of three floats, so
    # `elapsed == duration` lands a few ulps inside the fall rather than on
    # its boundary. Physically this is zero.
    assert stretch_amount(0.0, P) == 0.0
    assert stretch_amount(P.duration, P) == pytest.approx(0.0, abs=1e-9)
    assert stretch_amount(P.duration + 10.0, P) == 0.0


def test_reaches_full_stretch_during_the_hold():
    mid_hold = P.rise_time + P.hold_time / 2
    assert stretch_amount(mid_hold, P) == 1.0


def test_the_hold_actually_holds():
    """Without a sustained plateau this looks like a stumble, not a stretch."""
    a = stretch_amount(P.rise_time + 0.05, P)
    b = stretch_amount(P.rise_time + P.hold_time - 0.05, P)
    assert a == b == 1.0


def test_rises_monotonically_then_falls_monotonically():
    rise = [stretch_amount(P.rise_time * i / 20, P) for i in range(21)]
    assert rise == sorted(rise)
    start_fall = P.rise_time + P.hold_time
    fall = [stretch_amount(start_fall + P.fall_time * i / 20, P) for i in range(21)]
    assert fall == sorted(fall, reverse=True)


def test_release_is_slower_than_the_reach():
    """Cats collapse out of a stretch more lazily than they go into it."""
    assert P.fall_time > P.rise_time


# --- pose offsets ---------------------------------------------------------


def test_no_offset_at_zero_amount():
    assert stretch_offsets(0.0, True, P) == (0.0, 0.0)
    assert stretch_offsets(0.0, False, P) == (0.0, 0.0)


def test_front_feet_reach_forward_and_the_chest_drops():
    dx, dz = stretch_offsets(1.0, True, P)
    assert dx > 0, "front feet slide ahead of the shoulders"
    assert dz > 0, "positive dz shortens hip-to-foot, folding the front legs"


def test_rear_feet_shift_back_and_the_hips_rise():
    dx, dz = stretch_offsets(1.0, False, P)
    assert dx < 0
    assert dz < 0, "negative dz extends the rear legs, lifting the hips"


def test_front_and_rear_move_in_opposite_directions():
    """That opposition is what makes it a bow rather than a crouch."""
    front_dx, front_dz = stretch_offsets(1.0, True, P)
    rear_dx, rear_dz = stretch_offsets(1.0, False, P)
    assert front_dx * rear_dx < 0
    assert front_dz * rear_dz < 0


def test_offsets_scale_linearly_with_amount():
    half = stretch_offsets(0.5, True, P)
    full = stretch_offsets(1.0, True, P)
    assert half[0] == pytest.approx(full[0] / 2)
    assert half[1] == pytest.approx(full[1] / 2)


# --- state machine --------------------------------------------------------


def test_starts_inactive():
    assert not StretchState().active


def test_trigger_activates_it():
    s = StretchState()
    assert s.trigger()
    assert s.active


def test_retrigger_while_running_is_ignored():
    """Key autorepeat would otherwise pin the cat at the start of the pose."""
    s = StretchState()
    s.trigger()
    s.step(0.3)
    assert not s.trigger()


def test_it_finishes_and_goes_inactive():
    s = StretchState()
    s.trigger()
    for _ in range(int(P.duration / 0.01) + 5):
        s.step(0.01)
    assert not s.active
    assert s.step(0.01) == 0.0


def test_it_can_be_triggered_again_after_finishing():
    s = StretchState()
    s.trigger()
    for _ in range(int(P.duration / 0.01) + 5):
        s.step(0.01)
    assert s.trigger()


def test_stepping_while_inactive_is_zero():
    assert StretchState().step(0.1) == 0.0


def test_cancel_stops_it():
    s = StretchState()
    s.trigger()
    s.step(0.2)
    s.cancel()
    assert not s.active


def test_the_amount_peaks_at_one_over_a_full_run():
    s = StretchState()
    s.trigger()
    peak = max(s.step(0.01) for _ in range(int(P.duration / 0.01)))
    assert peak == pytest.approx(1.0)


# --- joint targets --------------------------------------------------------


def test_zero_amount_is_exactly_the_standing_pose():
    """Otherwise the cat would snap at the start and end of every stretch."""
    g = GaitGenerator()
    assert g.stretch_pose(0.0) == pytest.approx(g.stand())


def test_the_pose_stays_inside_the_joint_limits():
    """These come from cat.urdf.xacro; exceeding them means the controller
    fights a joint stop and the pose silently comes out wrong. Calf is
    mirrored for rear legs (see leg.xacro's knee_sign comment) - a real hind
    knee bends the opposite way from a front elbow."""
    limits = {
        "hip": (-0.80, 0.80),
        "thigh": (-1.45, 2.60),
        "calf": {"front": (-2.70, -0.10), "rear": (0.10, 2.70)},
    }
    g = GaitGenerator()
    for i in range(21):
        pose = g.stretch_pose(i / 20)
        for leg_idx, leg in enumerate(LEGS):
            for j, joint in enumerate(("hip", "thigh", "calf")):
                value = pose[leg_idx * 3 + j]
                if joint == "calf":
                    lo, hi = limits["calf"]["front" if X_SIGN[leg] > 0 else "rear"]
                else:
                    lo, hi = limits[joint]
                assert lo <= value <= hi, f"{leg}_{joint} at amount {i/20}: {value}"


def test_the_front_legs_fold_more_than_the_rear():
    """The bow shape, read back off the joints rather than the offsets."""
    g = GaitGenerator()
    targets = dict(zip(JOINT_ORDER, g.stretch_pose(1.0)))
    assert abs(targets["fl_calf_joint"]) > abs(targets["rl_calf_joint"])
