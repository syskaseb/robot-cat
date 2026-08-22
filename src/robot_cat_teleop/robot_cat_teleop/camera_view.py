"""Cycle the Gazebo GUI camera between free, third-person and first-person.

Talks to the GUI over gz-transport rather than ROS: the viewport camera is a
gz-sim concept with no ROS bridge.

The two tracked views work in completely different ways, because Gazebo's
built-in follow cannot do first-person:

* **third-person** uses ``/gui/follow`` plus ``/gui/follow/offset``. Follow
  parents the camera to the model at an offset and keeps it pointed *at* the
  model, which is exactly a chase cam.
* **first-person** cannot use follow for that same reason - a camera that
  always looks at the cat can never look out through its eyes. So the camera
  pose is driven directly instead: a background thread reads link poses off
  ``dynamic_pose/info``, composes the head's world pose, and pushes it to
  ``/gui/move_to/pose`` about 20 times a second. The head's orientation
  becomes the camera's, so W/A/S/D turn the view exactly as they turn the
  head.

Driving the camera from a thread is deliberate: the request is synchronous
and would otherwise stall the teleop key loop.
"""

from __future__ import annotations

import math
import re
import threading
from enum import Enum, auto

from gz.msgs10.boolean_pb2 import Boolean
from gz.msgs10.gui_camera_pb2 import GUICamera
from gz.msgs10.pose_v_pb2 import Pose_V
from gz.msgs10.stringmsg_pb2 import StringMsg
from gz.msgs10.vector3d_pb2 import Vector3d
from gz.transport13 import Node

_MOVE_TO_POSE = "/gui/move_to/pose"
_FOLLOW = "/gui/follow"
_FOLLOW_OFFSET = "/gui/follow/offset"
_TIMEOUT_MS = 300

#: Chase-cam offset in the cat's own frame: behind (-x) and above (+z).
_THIRD_PERSON_OFFSET = (-0.55, 0.0, 0.18)

#: Eye position relative to head_link. The head is a 0.05 m sphere centred on
#: that origin, so anything much under 0.10 m puts the camera inside the
#: cat's own skull and the dome fills the bottom of the frame.
_EYE_OFFSET = (0.12, 0.0, 0.035)

_FIRST_PERSON_HZ = 20.0

MODEL_NAME = "robot_cat"
HEAD_LINK = "head_link"


def quat_multiply(
    a: tuple[float, float, float, float], b: tuple[float, float, float, float]
) -> tuple[float, float, float, float]:
    """Hamilton product of two (x, y, z, w) quaternions."""
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def quat_rotate(
    q: tuple[float, float, float, float], v: tuple[float, float, float]
) -> tuple[float, float, float]:
    """Rotate vector ``v`` by quaternion ``q`` (x, y, z, w)."""
    x, y, z, w = q
    vx, vy, vz = v
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    return (
        vx + w * tx + (y * tz - z * ty),
        vy + w * ty + (z * tx - x * tz),
        vz + w * tz + (x * ty - y * tx),
    )


def head_camera_pose(
    model_pos: tuple[float, float, float],
    model_quat: tuple[float, float, float, float],
    head_pos: tuple[float, float, float],
    head_quat: tuple[float, float, float, float],
    eye_offset: tuple[float, float, float] = _EYE_OFFSET,
) -> tuple[tuple[float, float, float], tuple[float, float, float, float]]:
    """Compose the world pose of the cat's eyes.

    ``dynamic_pose/info`` reports link poses in the model frame and the model
    pose in the world frame, so the two have to be chained.

    Returns:
        ``(position, orientation)`` in the world frame.
    """
    world_quat = quat_multiply(model_quat, head_quat)
    head_world = quat_rotate(model_quat, head_pos)
    eye = quat_rotate(world_quat, eye_offset)
    position = (
        model_pos[0] + head_world[0] + eye[0],
        model_pos[1] + head_world[1] + eye[1],
        model_pos[2] + head_world[2] + eye[2],
    )
    return position, world_quat


class CameraView(Enum):
    FREE = auto()
    THIRD_PERSON = auto()
    FIRST_PERSON = auto()


class CameraController:
    """Owns the gz-transport node and the first-person driver thread."""

    def __init__(self, world: str | None = None) -> None:
        self._node = Node()
        self._view = CameraView.FREE
        self._world = world
        self._poses: dict[str, tuple] = {}
        self._subscribed = False
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def view(self) -> CameraView:
        return self._view

    def cycle(self) -> CameraView:
        order = [CameraView.FREE, CameraView.THIRD_PERSON, CameraView.FIRST_PERSON]
        self._view = order[(order.index(self._view) + 1) % len(order)]
        self._apply(self._view)
        return self._view

    def shutdown(self) -> None:
        self._stop_first_person()

    # -- view plumbing ----------------------------------------------------

    def _apply(self, view: CameraView) -> None:
        if view is not CameraView.FIRST_PERSON:
            self._stop_first_person()

        if view is CameraView.THIRD_PERSON:
            self._set_follow(MODEL_NAME, _THIRD_PERSON_OFFSET)
        elif view is CameraView.FIRST_PERSON:
            self._set_follow("", None)  # follow would keep aiming at the cat
            self._start_first_person()
        else:
            self._set_follow("", None)

    def _set_follow(
        self, name: str, offset: tuple[float, float, float] | None
    ) -> None:
        msg = StringMsg()
        msg.data = name
        self._try(_FOLLOW, msg, StringMsg)
        if offset is None:
            return
        vec = Vector3d()
        vec.x, vec.y, vec.z = offset
        self._try(_FOLLOW_OFFSET, vec, Vector3d)

    def _try(self, service: str, req, req_type) -> None:
        """A dropped view change is a UI nuisance, not a reason to kill teleop."""
        try:
            self._node.request(service, req, req_type, Boolean, _TIMEOUT_MS)
        except Exception:
            pass

    # -- first person -----------------------------------------------------

    def _world_name(self) -> str | None:
        """Discover the running world, so this works in any of them."""
        if self._world:
            return self._world
        try:
            for topic in self._node.topic_list():
                match = re.fullmatch(r"/world/([^/]+)/dynamic_pose/info", topic)
                if match:
                    self._world = match.group(1)
                    return self._world
        except Exception:
            pass
        return None

    def _on_poses(self, msg: Pose_V) -> None:
        for pose in msg.pose:
            if pose.name in (MODEL_NAME, HEAD_LINK):
                self._poses[pose.name] = (
                    (pose.position.x, pose.position.y, pose.position.z),
                    (
                        pose.orientation.x,
                        pose.orientation.y,
                        pose.orientation.z,
                        pose.orientation.w,
                    ),
                )

    def _start_first_person(self) -> None:
        world = self._world_name()
        if world is None:
            return
        if not self._subscribed:
            try:
                self._node.subscribe(
                    Pose_V, f"/world/{world}/dynamic_pose/info", self._on_poses
                )
                self._subscribed = True
            except Exception:
                return

        self._stop.clear()
        self._thread = threading.Thread(target=self._drive, daemon=True)
        self._thread.start()

    def _stop_first_person(self) -> None:
        self._stop.set()
        thread, self._thread = self._thread, None
        if thread is not None:
            thread.join(timeout=1.0)

    def _drive(self) -> None:
        period = 1.0 / _FIRST_PERSON_HZ
        while not self._stop.wait(period):
            model = self._poses.get(MODEL_NAME)
            head = self._poses.get(HEAD_LINK)
            if model is None or head is None:
                continue
            position, orientation = head_camera_pose(
                model[0], model[1], head[0], head[1]
            )
            req = GUICamera()
            req.pose.position.x, req.pose.position.y, req.pose.position.z = position
            (
                req.pose.orientation.x,
                req.pose.orientation.y,
                req.pose.orientation.z,
                req.pose.orientation.w,
            ) = orientation
            self._try(_MOVE_TO_POSE, req, GUICamera)
