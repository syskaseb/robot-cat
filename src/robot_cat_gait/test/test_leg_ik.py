"""IK correctness: every solution must round-trip through forward kinematics."""

import math

import pytest

from robot_cat_gait.leg_ik import LegGeometry, leg_fk, leg_ik

GEOM = LegGeometry()


@pytest.mark.parametrize("y_sign", [1.0, -1.0])
@pytest.mark.parametrize(
    "x,z",
    [
        (0.0, -0.13),     # neutral stance
        (0.04, -0.12),    # foot forward
        (-0.04, -0.12),   # foot back
        (0.0, -0.16),     # tall stance
        (0.0, -0.10),     # crouched
        (0.05, -0.145),   # extended reach
    ],
)
def test_ik_round_trips(x, z, y_sign):
    y = y_sign * GEOM.hip_offset
    q = leg_ik(x, y, z, GEOM, y_sign)
    back = leg_fk(*q, GEOM, y_sign)
    assert back == pytest.approx((x, y, z), abs=1e-9)


@pytest.mark.parametrize("y_sign", [1.0, -1.0])
def test_ik_round_trips_with_hip_roll(y_sign):
    """Targets off the leg's sagittal plane exercise the hip roll joint."""
    for y_extra in (0.02, -0.02, 0.045):
        y = y_sign * GEOM.hip_offset + y_extra
        q = leg_ik(0.01, y, -0.13, GEOM, y_sign)
        assert q[0] != 0.0, "hip roll should be non-zero for an off-plane target"
        assert leg_fk(*q, GEOM, y_sign) == pytest.approx((0.01, y, -0.13), abs=1e-9)


def test_left_and_right_legs_mirror():
    q_left = leg_ik(0.03, GEOM.hip_offset + 0.02, -0.13, GEOM, 1.0)
    q_right = leg_ik(0.03, -(GEOM.hip_offset + 0.02), -0.13, GEOM, -1.0)
    assert q_left[0] == pytest.approx(-q_right[0])   # hip roll mirrors
    assert q_left[1] == pytest.approx(q_right[1])    # pitches do not
    assert q_left[2] == pytest.approx(q_right[2])


def test_unreachable_target_saturates_instead_of_raising():
    """A target beyond the leg's reach must clamp, not blow up the controller."""
    far = GEOM.max_reach * 3.0
    q = leg_ik(0.0, GEOM.hip_offset, -far, GEOM, 1.0)
    assert all(math.isfinite(v) for v in q)
    # Fully extended: the knee straightens.
    assert q[2] == pytest.approx(0.0, abs=1e-9)


def test_knee_sign_selects_the_other_branch():
    a = leg_ik(0.0, GEOM.hip_offset, -0.13, GEOM, 1.0, knee_sign=-1.0)
    b = leg_ik(0.0, GEOM.hip_offset, -0.13, GEOM, 1.0, knee_sign=+1.0)
    assert a[2] == pytest.approx(-b[2])
    # Both branches are valid IK solutions.
    assert leg_fk(*b, GEOM, 1.0) == pytest.approx((0.0, GEOM.hip_offset, -0.13), abs=1e-9)


def test_turn_radius_is_the_distance_to_a_neutral_foot():
    geom = LegGeometry(mount_x=0.11, mount_y=0.055, hip_offset=0.035)
    assert geom.foot_y == pytest.approx(0.09)
    assert geom.turn_radius == pytest.approx(math.hypot(0.11, 0.09))
