"""The loaf: a toggle that eases smoothly to lying and back, and reverses
cleanly if the second press lands mid-transition.
"""

import pytest

from robot_cat_gait.gait import JOINT_ORDER, LEGS, X_SIGN, GaitGenerator
from robot_cat_gait.lie_down import LieDownParams, LieDownState

P = LieDownParams()


# --- the toggle -------------------------------------------------------


def test_starts_standing():
    s = LieDownState()
    assert not s.down
    assert s.amount == 0.0


def test_toggle_targets_lying_and_reports_it():
    s = LieDownState()
    assert s.toggle() is True
    assert s.down


def test_toggling_twice_returns_to_standing():
    s = LieDownState()
    s.toggle()
    assert s.toggle() is False
    assert not s.down


def test_force_stand_overrides_a_lying_target():
    s = LieDownState()
    s.toggle()
    s.force_stand()
    assert not s.down


def test_force_stand_is_a_no_op_when_already_standing():
    s = LieDownState()
    s.force_stand()
    assert not s.down


# --- easing toward the target ------------------------------------------


def test_amount_moves_toward_the_target():
    s = LieDownState()
    s.toggle()
    a = s.step(0.1)
    assert 0.0 < a < 1.0


def test_amount_settles_near_one_when_left_down():
    s = LieDownState()
    s.toggle()
    for _ in range(200):
        s.step(0.05)
    assert s.amount == pytest.approx(1.0, abs=1e-3)


def test_amount_settles_near_zero_after_standing_back_up():
    s = LieDownState()
    s.toggle()
    for _ in range(200):
        s.step(0.05)
    s.toggle()
    for _ in range(200):
        s.step(0.05)
    assert s.amount == pytest.approx(0.0, abs=1e-3)


def test_reversing_mid_transition_does_not_jump():
    """The whole point of easing the amount rather than following a fixed
    schedule: a reversal must continue from wherever motion currently is,
    not snap back to either end first."""
    s = LieDownState()
    s.toggle()
    s.step(0.3)
    mid = s.amount
    assert 0.0 < mid < 1.0
    s.toggle()
    a = s.step(0.001)
    assert a == pytest.approx(mid, abs=1e-3), "must not have jumped on reversal"


def test_reversing_mid_transition_then_heads_back_down():
    s = LieDownState()
    s.toggle()
    s.step(0.3)
    s.toggle()  # reverse toward standing
    before = s.amount
    after = s.step(0.05)
    assert after < before


def test_a_zero_or_negative_tau_snaps_instead_of_dividing_by_zero():
    s = LieDownState(LieDownParams(tau=0.0))
    s.toggle()
    assert s.step(0.01) == 1.0


# --- joint targets -------------------------------------------------------


def test_zero_amount_is_exactly_the_standing_pose():
    g = GaitGenerator()
    assert g.lie_pose(0.0) == pytest.approx(g.stand())


def test_full_amount_uses_the_down_stance_height():
    """Read back through forward kinematics rather than asserting on raw
    joint angles, which would just re-encode the IK by hand."""
    from robot_cat_gait.leg_ik import leg_fk

    g = GaitGenerator()
    targets = g.lie_pose(1.0)
    qh, qt, qc = targets[0:3]  # fl
    _, y, z = leg_fk(qh, qt, qc, g.geom, y_sign=1.0)
    assert -z == pytest.approx(P.down_stance_height, abs=1e-6)


def test_the_pose_stays_inside_the_joint_limits():
    # Calf is mirrored for rear legs (see leg.xacro's knee_sign comment) - a
    # real hind knee bends the opposite way from a front elbow.
    limits = {
        "hip": (-0.80, 0.80),
        "thigh": (-1.45, 2.60),
        "calf": {"front": (-2.70, -0.10), "rear": (0.10, 2.70)},
    }
    g = GaitGenerator()
    for i in range(21):
        for leg in LEGS:
            for name, value in zip(
                JOINT_ORDER[LEGS.index(leg) * 3 : LEGS.index(leg) * 3 + 3],
                g.lie_pose(i / 20)[LEGS.index(leg) * 3 : LEGS.index(leg) * 3 + 3],
            ):
                joint = name.split("_")[1]
                if joint == "calf":
                    lo, hi = limits["calf"]["front" if X_SIGN[leg] > 0 else "rear"]
                else:
                    lo, hi = limits[joint]
                assert lo <= value <= hi, f"{name} at amount {i/20}: {value}"


def test_the_pose_leaves_real_margin_to_the_calf_stop():
    """0.04 m leaves only 0.007 rad of headroom on the calf stop (see the
    down_stance_height docstring) - guard the margin, not just the limit,
    so a future retune cannot quietly reintroduce that near-miss."""
    g = GaitGenerator()
    calf = g.lie_pose(1.0)[2]  # fl_calf_joint
    assert calf > -2.70 + 0.05


def test_the_pose_leaves_real_margin_to_the_rear_thigh_stop():
    """The rear leg's mirrored knee needs the thigh to swing much further
    negative than the front leg ever does, which is exactly what clipped
    thigh_lower at -1.20 during development - see the property's comment in
    cat.urdf.xacro. Guard the margin, not just the limit."""
    g = GaitGenerator()
    thigh = g.lie_pose(1.0)[7]  # rl_thigh_joint
    assert thigh > -1.45 + 0.05


def test_all_four_legs_match_at_full_amount():
    """Symmetric front-to-back is what makes this a loaf and not a stretch -
    read through forward kinematics, since the joint *angles* legitimately
    differ front-to-back now (rear knees bend the opposite way), even though
    the feet land at the same offset from their hips."""
    from robot_cat_gait.leg_ik import leg_fk

    g = GaitGenerator()
    targets = dict(zip(JOINT_ORDER, g.lie_pose(1.0)))
    front = leg_fk(
        targets["fl_hip_joint"], targets["fl_thigh_joint"], targets["fl_calf_joint"],
        g.geom, y_sign=1.0,
    )
    rear = leg_fk(
        targets["rl_hip_joint"], targets["rl_thigh_joint"], targets["rl_calf_joint"],
        g.geom, y_sign=1.0,
    )
    assert front[0] == pytest.approx(rear[0], abs=1e-9)
    assert front[2] == pytest.approx(rear[2], abs=1e-9)
