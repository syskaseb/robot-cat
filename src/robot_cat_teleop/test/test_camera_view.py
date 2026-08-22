"""Camera view cycling, and the pose maths behind the first-person view.

The gz-transport calls are stubbed so the cycle order and the service
payloads can be asserted without a running simulator. The quaternion helpers
are exercised directly - getting the model/link chaining wrong puts the
camera somewhere plausible-looking but subtly detached from the cat, which
is hard to spot by eye.
"""

import math

import pytest

from robot_cat_teleop.camera_view import (
    CameraController,
    CameraView,
    head_camera_pose,
    quat_multiply,
    quat_rotate,
)

IDENTITY = (0.0, 0.0, 0.0, 1.0)


def yaw_quat(angle: float) -> tuple[float, float, float, float]:
    return (0.0, 0.0, math.sin(angle / 2), math.cos(angle / 2))


def approx(actual, expected, tol=1e-6):
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert a == pytest.approx(e, abs=tol)


# --- quaternion helpers --------------------------------------------------


def test_identity_quaternion_leaves_a_vector_alone():
    approx(quat_rotate(IDENTITY, (1.0, 2.0, 3.0)), (1.0, 2.0, 3.0))


def test_quarter_turn_about_z_maps_x_to_y():
    approx(quat_rotate(yaw_quat(math.pi / 2), (1.0, 0.0, 0.0)), (0.0, 1.0, 0.0))


def test_multiplying_two_quarter_turns_gives_a_half_turn():
    q = quat_multiply(yaw_quat(math.pi / 2), yaw_quat(math.pi / 2))
    approx(quat_rotate(q, (1.0, 0.0, 0.0)), (-1.0, 0.0, 0.0))


def test_multiplying_by_identity_changes_nothing():
    q = yaw_quat(0.7)
    approx(quat_multiply(q, IDENTITY), q)


# --- head pose composition ----------------------------------------------


def test_eye_sits_ahead_of_the_head_when_everything_is_unrotated():
    pos, quat = head_camera_pose(
        (0.0, 0.0, 0.0), IDENTITY, (0.18, 0.0, 0.045), IDENTITY,
        eye_offset=(0.06, 0.0, 0.02),
    )
    approx(pos, (0.24, 0.0, 0.065))
    approx(quat, IDENTITY)


def test_model_translation_carries_the_camera_with_it():
    pos, _ = head_camera_pose(
        (5.0, -2.0, 0.14), IDENTITY, (0.18, 0.0, 0.045), IDENTITY,
        eye_offset=(0.0, 0.0, 0.0),
    )
    approx(pos, (5.18, -2.0, 0.185))


def test_model_yaw_rotates_the_head_offset_into_the_world():
    """The head is 0.18 m along the cat's own +x; turn the cat 90 deg and
    that offset must come out along world +y, not stay on +x."""
    pos, quat = head_camera_pose(
        (0.0, 0.0, 0.0), yaw_quat(math.pi / 2), (0.18, 0.0, 0.0), IDENTITY,
        eye_offset=(0.0, 0.0, 0.0),
    )
    approx(pos, (0.0, 0.18, 0.0))
    approx(quat, yaw_quat(math.pi / 2))


def test_head_pan_adds_to_model_yaw():
    """Panning the head 90 deg on a cat already turned 90 deg must look
    backwards along world -x - this is the composition the view depends on."""
    _, quat = head_camera_pose(
        (0.0, 0.0, 0.0), yaw_quat(math.pi / 2), (0.0, 0.0, 0.0),
        yaw_quat(math.pi / 2),
    )
    approx(quat_rotate(quat, (1.0, 0.0, 0.0)), (-1.0, 0.0, 0.0))


def test_eye_offset_follows_the_head_not_the_world():
    """With the head panned, the eye must move sideways in the world."""
    pos, _ = head_camera_pose(
        (0.0, 0.0, 0.0), IDENTITY, (0.0, 0.0, 0.0), yaw_quat(math.pi / 2),
        eye_offset=(0.06, 0.0, 0.0),
    )
    approx(pos, (0.0, 0.06, 0.0))


# --- view cycling --------------------------------------------------------


@pytest.fixture
def controller(monkeypatch):
    sent = []

    def fake_request(self, service, req, req_type, resp_type, timeout):
        sent.append((service, req))
        return True, None

    monkeypatch.setattr(
        "robot_cat_teleop.camera_view.Node.request", fake_request, raising=False
    )
    monkeypatch.setattr(
        CameraController, "_start_first_person", lambda self: None
    )
    c = CameraController(world="test_world")
    c.sent = sent
    return c


def services(controller):
    return [s for s, _ in controller.sent]


def test_starts_free(controller):
    assert controller.view is CameraView.FREE


def test_cycles_free_third_first_and_wraps(controller):
    assert controller.cycle() is CameraView.THIRD_PERSON
    assert controller.cycle() is CameraView.FIRST_PERSON
    assert controller.cycle() is CameraView.FREE


def test_third_person_follows_the_model_from_behind_and_above(controller):
    controller.cycle()
    follow = [r for s, r in controller.sent if s == "/gui/follow"][-1]
    offset = [r for s, r in controller.sent if s == "/gui/follow/offset"][-1]
    assert follow.data == "robot_cat"
    assert offset.x < 0, "chase cam sits behind the cat"
    assert offset.z > 0, "and above it"


def test_first_person_releases_follow(controller):
    """Follow always aims the camera at the cat, so it must be off before
    the pose driver takes over - otherwise the two fight."""
    controller.cycle()
    controller.cycle()
    follow = [r for s, r in controller.sent if s == "/gui/follow"][-1]
    assert follow.data == ""


def test_free_releases_follow(controller):
    for _ in range(3):
        controller.cycle()
    follow = [r for s, r in controller.sent if s == "/gui/follow"][-1]
    assert follow.data == ""


def test_a_failing_request_does_not_propagate(monkeypatch):
    def boom(self, service, req, req_type, resp_type, timeout):
        raise RuntimeError("gz-transport is down")

    monkeypatch.setattr(
        "robot_cat_teleop.camera_view.Node.request", boom, raising=False
    )
    monkeypatch.setattr(
        CameraController, "_start_first_person", lambda self: None
    )
    c = CameraController(world="test_world")
    assert c.cycle() is CameraView.THIRD_PERSON
