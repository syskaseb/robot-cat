"""The tail sweep is a small state machine driven by one key, so the parts
worth pinning down are the reversals: that a press landing on a limit stops
there, and that the press after it goes back the other way."""

from robot_cat_teleop.tail import TailParams, TailState


def settle(tail: TailState, steps: int = 400) -> float:
    """Run the filter until it has essentially reached its target."""
    for _ in range(steps):
        tail.step(dt=0.02)
    return tail.angle


def test_starts_at_rest():
    tail = TailState()
    assert tail.angle == 0.0
    assert tail.target == 0.0


def test_first_press_lowers_because_rest_pose_is_tail_up():
    tail = TailState()
    assert tail.press() < 0.0


def test_each_press_moves_one_step():
    params = TailParams(step=0.3)
    tail = TailState(params)
    assert tail.press() == -0.3
    assert round(tail.press(), 10) == -0.6
    assert round(tail.press(), 10) == -0.9


def test_press_landing_on_the_minimum_stops_there():
    params = TailParams(min_angle=-0.6, max_angle=0.9, step=0.3)
    tail = TailState(params)
    tail.press()
    assert tail.press() == params.min_angle


def test_press_after_the_minimum_raises_again():
    params = TailParams(min_angle=-0.6, max_angle=0.9, step=0.3)
    tail = TailState(params)
    tail.press()
    tail.press()
    assert tail.target == params.min_angle
    assert tail.press() > params.min_angle


def test_press_after_the_maximum_lowers_again():
    params = TailParams(min_angle=-0.3, max_angle=0.3, step=0.3)
    tail = TailState(params)
    tail.press()                      # down to min
    assert tail.target == params.min_angle
    tail.press()                      # reversed: up to 0.0
    tail.press()                      # up to max
    assert tail.target == params.max_angle
    assert tail.press() < params.max_angle


def test_overshooting_step_is_clamped_to_the_limit():
    """A step larger than the remaining travel must not sail past the end."""
    params = TailParams(min_angle=-0.4, max_angle=0.9, step=1.0)
    tail = TailState(params)
    assert tail.press() == params.min_angle


def test_sweep_never_leaves_the_configured_range():
    params = TailParams(min_angle=-1.2, max_angle=0.9, step=0.3)
    tail = TailState(params)
    for _ in range(200):
        target = tail.press()
        assert params.min_angle <= target <= params.max_angle


def test_full_sweep_reaches_both_ends():
    params = TailParams(min_angle=-1.2, max_angle=0.9, step=0.3)
    tail = TailState(params)
    seen = {round(tail.press(), 10) for _ in range(60)}
    assert params.min_angle in seen
    assert params.max_angle in seen


def test_direction_flag_tracks_the_sweep():
    params = TailParams(min_angle=-0.3, max_angle=0.3, step=0.3)
    tail = TailState(params)
    assert tail.direction == -1.0
    tail.press()
    assert tail.direction == 1.0


def test_angle_eases_toward_the_target_rather_than_jumping():
    tail = TailState()
    tail.press()
    after_one_tick = tail.step(dt=0.02)
    assert tail.target < after_one_tick < 0.0


def test_angle_settles_on_the_target():
    tail = TailState()
    tail.press()
    assert abs(settle(tail) - tail.target) < 1e-9


def test_angle_follows_a_reversal_back_up():
    params = TailParams(min_angle=-0.3, max_angle=0.3, step=0.3)
    tail = TailState(params)
    tail.press()
    settle(tail)
    assert abs(tail.angle - params.min_angle) < 1e-9

    tail.press()
    settle(tail)
    assert tail.angle > params.min_angle


def test_presses_during_motion_still_accumulate():
    """Pressing again before the tail has arrived must move the target, not
    wait for the previous move to finish."""
    tail = TailState(TailParams(step=0.3))
    tail.press()
    tail.step(dt=0.01)
    tail.press()
    assert round(tail.target, 10) == -0.6
