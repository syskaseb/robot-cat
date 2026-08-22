"""HeadState is what makes W/A/S/D look like a cat looking around instead of
a servo snapping to a setpoint. These tests pin down the easing and the
limits, not the exact numeric trajectory."""

from robot_cat_teleop.head import HeadParams, HeadState


def test_no_input_stays_at_rest():
    head = HeadState()
    for _ in range(20):
        pan, tilt = head.step(dt=0.05, pan_dir=0.0, tilt_dir=0.0)
    assert pan == 0.0
    assert tilt == 0.0


def test_holding_a_direction_eventually_moves_that_way():
    head = HeadState()
    for _ in range(200):
        pan, tilt = head.step(dt=0.02, pan_dir=1.0, tilt_dir=0.0)
    assert pan > 0.0
    assert tilt == 0.0


def test_motion_ramps_up_rather_than_snapping():
    """The very first tick should move far less than a later tick once the
    velocity filter has caught up - that gap is the "natural" ease-in.

    Few enough steps that pan stays well clear of its limit - this test is
    about the ramp shape, not clamping."""
    head = HeadState()
    first_pan, _ = head.step(dt=0.02, pan_dir=1.0, tilt_dir=0.0)
    for _ in range(15):
        prev_pan = head.pan
        pan, _ = head.step(dt=0.02, pan_dir=1.0, tilt_dir=0.0)
    later_step = pan - prev_pan
    first_step = first_pan
    assert first_step < later_step


def test_releasing_the_key_decelerates_rather_than_stopping_dead():
    head = HeadState()
    for _ in range(15):
        head.step(dt=0.02, pan_dir=1.0, tilt_dir=0.0)
    moving_vel = head._pan_vel
    assert moving_vel > 0.0

    head.step(dt=0.02, pan_dir=0.0, tilt_dir=0.0)
    assert 0.0 < head._pan_vel < moving_vel


def test_pan_clamps_to_configured_range():
    params = HeadParams(pan_lower=-0.2, pan_upper=0.2, velocity_tau=0.01)
    head = HeadState(params)
    for _ in range(500):
        pan, _ = head.step(dt=0.05, pan_dir=1.0, tilt_dir=0.0)
    assert pan == params.pan_upper


def test_tilt_clamps_to_configured_range():
    params = HeadParams(tilt_lower=-0.2, tilt_upper=0.2, velocity_tau=0.01)
    head = HeadState(params)
    for _ in range(500):
        _, tilt = head.step(dt=0.05, pan_dir=0.0, tilt_dir=-1.0)
    assert tilt == params.tilt_lower


def test_velocity_zeroed_at_limit_so_release_does_not_jerk_back():
    params = HeadParams(pan_lower=-0.2, pan_upper=0.2, velocity_tau=0.01)
    head = HeadState(params)
    for _ in range(500):
        head.step(dt=0.05, pan_dir=1.0, tilt_dir=0.0)
    assert head.pan == params.pan_upper
    assert head._pan_vel == 0.0


def test_opposite_keys_cancel_via_direction_clamp():
    """The teleop node maps "both held" to whichever branch it prefers, but
    HeadState itself must also behave sanely if asked for an out-of-range
    direction."""
    head = HeadState()
    pan, _ = head.step(dt=0.05, pan_dir=2.0, tilt_dir=0.0)
    only_one_direction = HeadState().step(dt=0.05, pan_dir=1.0, tilt_dir=0.0)[0]
    assert pan == only_one_direction
