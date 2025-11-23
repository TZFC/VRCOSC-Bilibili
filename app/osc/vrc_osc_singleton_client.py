"""
A singleton VRChatOSC API

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.

Notes:
  - AI assistance was used in drafting parts of this file.
"""
import logging
import math
import threading
from typing import Optional

from app.osc.vrc_osc import VRChatOSC
from app.Utils.config_loader import CONFIG

logger = logging.getLogger(__name__)

_vrc: Optional[VRChatOSC] = None

_last_camera_pose: Optional[tuple[float, float, float, float, float, float]] = None
_last_camera_pose_lock = threading.Lock()
_listener_started = False

_vrc_listen_port = 9001  # Assumes VRChat default OSC receive port

def _ensure_ready() -> VRChatOSC:
    """
    Ensure a single VRChat OSC connection exist
    """
    global _vrc
    if _vrc is None:
        logger.debug("first-time setup of VRChatOSC client")
        _vrc = VRChatOSC.connect(ip = CONFIG["LAN_ip"], port = CONFIG["LAN_port"])
    return _vrc

def _camera_pose_handler(message_address: str, *message_arguments: float) -> None:
    """
    Internal handler that stores the last received camera pose from VRChat.
    """
    global _last_camera_pose
    if message_address != "/usercamera/Pose":
        return
    if len(message_arguments) != 6:
        logger.warning(
            "Received /usercamera/Pose with %d arguments, expected 6",
            len(message_arguments),
        )
        return
    pose_tuple = tuple(float(value) for value in message_arguments)
    with _last_camera_pose_lock:
        _last_camera_pose = pose_tuple
    logger.debug("updated last_camera_pose = %r", pose_tuple)


def _ensure_listener_started() -> None:
    """
    Ensure the Open Sound Control listener is running and subscribed to /usercamera/Pose.
    """
    global _listener_started
    if _listener_started:
        return

    vrchat_open_sound_control = _ensure_ready()
    vrchat_open_sound_control.start_listening(
        listen_port=_vrc_listen_port,
    )
    vrchat_open_sound_control.add_handler(
        "/usercamera/Pose",
        _camera_pose_handler,
    )
    _listener_started = True
    logger.info(
        "OSC listener started on port %d and subscribed to /usercamera/Pose",
        _vrc_listen_port,
    )


def _compute_local_direction_vectors_from_euler(
    rotation_x_degrees: float,
    rotation_y_degrees: float,
) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    """
    Compute forward, right, and up direction vectors from camera Euler rotation.

    This uses a common convention:
      - rotation_y_degrees is yaw around the up axis
      - rotation_x_degrees is pitch around the right axis
    """
    yaw_radians = math.radians(rotation_y_degrees)
    pitch_radians = math.radians(rotation_x_degrees)

    forward_vector_x = math.cos(pitch_radians) * math.sin(yaw_radians)
    forward_vector_y = math.sin(pitch_radians)
    forward_vector_z = math.cos(pitch_radians) * math.cos(yaw_radians)

    right_vector_x = math.cos(yaw_radians)
    right_vector_y = 0.0
    right_vector_z = -math.sin(yaw_radians)

    up_vector_x = (
        forward_vector_y * right_vector_z - forward_vector_z * right_vector_y
    )
    up_vector_y = (
        forward_vector_z * right_vector_x - forward_vector_x * right_vector_z
    )
    up_vector_z = (
        forward_vector_x * right_vector_y - forward_vector_y * right_vector_x
    )

    return (
        (forward_vector_x, forward_vector_y, forward_vector_z),
        (right_vector_x, right_vector_y, right_vector_z),
        (up_vector_x, up_vector_y, up_vector_z),
    )

def update_parameter(name: str, value) -> None:
    """
    update the only Client's parameter with given value
    """
    _ensure_ready().update_parameter(name, value)


def send_chat(message: str, immediate: bool = True) -> None:
    """
    update the only Client's chatbox with given value
    """
    _ensure_ready().send_chat(message, immediate)

def move_camera(command_name: str, distance_value: float) -> None:
    """
    Move the camera relative to its current pose based on a simple command.

    Supported command_name values:
      - "left"
      - "right"
      - "up"
      - "down"
      - "close"
      - "far"

    distance_value is in world units (meters).
    """
    _ensure_listener_started()

    with _last_camera_pose_lock:
        current_pose = _last_camera_pose

    if current_pose is None:
        raise RuntimeError(
            "No camera pose has been received yet from VRChat "
            "for /usercamera/Pose."
        )

    (
        position_x,
        position_y,
        position_z,
        rotation_x,
        rotation_y,
        rotation_z,
    ) = current_pose

    (
        forward_vector,
        right_vector,
        up_vector,
    ) = _compute_local_direction_vectors_from_euler(rotation_x, rotation_y)

    if command_name == "left":
        direction_vector = (
            -right_vector[0],
            -right_vector[1],
            -right_vector[2],
        )
    elif command_name == "right":
        direction_vector = (
            right_vector[0],
            right_vector[1],
            right_vector[2],
        )
    elif command_name == "up":
        direction_vector = (
            up_vector[0],
            up_vector[1],
            up_vector[2],
        )
    elif command_name == "down":
        direction_vector = (
            -up_vector[0],
            -up_vector[1],
            -up_vector[2],
        )
    elif command_name == "close":
        direction_vector = (
            forward_vector[0],
            forward_vector[1],
            forward_vector[2],
        )
    elif command_name == "far":
        direction_vector = (
            -forward_vector[0],
            -forward_vector[1],
            -forward_vector[2],
        )
    else:
        raise ValueError(f"Unknown camera move command_name: {command_name!r}")

    new_position_x = position_x + direction_vector[0] * distance_value
    new_position_y = position_y + direction_vector[1] * distance_value
    new_position_z = position_z + direction_vector[2] * distance_value

    new_pose = [
        float(new_position_x),
        float(new_position_y),
        float(new_position_z),
        float(rotation_x),
        float(rotation_y),
        float(rotation_z),
    ]

    logger.debug(
        "move_camera %s %f: %r -> %r",
        command_name,
        distance_value,
        current_pose,
        new_pose,
    )

    _ensure_ready().update_camera("Pose", new_pose)
    
def close() -> None:
    """
    close the only Client
    """
    global _vrc
    if _vrc is not None:
        _vrc.close()
        _vrc = None
