"""Both the head and the tail lean on these two helpers, so a bug here shows
up as "the cat moves oddly" in two unrelated places."""

from robot_cat_teleop.smoothing import clamp, ease


def test_ease_moves_toward_target_but_not_past_it():
    assert 0.0 < ease(0.0, 1.0, dt=0.05, tau=0.12) < 1.0


def test_ease_reaches_target_when_dt_exceeds_tau():
    assert ease(0.0, 1.0, dt=10.0, tau=0.12) == 1.0


def test_ease_handles_zero_tau_as_instant():
    assert ease(0.0, 0.7, dt=0.01, tau=0.0) == 0.7


def test_ease_is_symmetric_downwards():
    assert -1.0 < ease(0.0, -1.0, dt=0.05, tau=0.12) < 0.0


def test_ease_at_target_is_a_no_op():
    assert ease(0.5, 0.5, dt=0.05, tau=0.12) == 0.5


def test_clamp():
    assert clamp(5.0, -1.0, 1.0) == 1.0
    assert clamp(-5.0, -1.0, 1.0) == -1.0
    assert clamp(0.3, -1.0, 1.0) == 0.3
