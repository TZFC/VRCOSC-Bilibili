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
from typing import Optional
from app.osc.vrc_osc import VRChatOSC

logger = logging.getLogger(__name__)
_vrc: Optional[VRChatOSC] = None


def _ensure_ready() -> VRChatOSC:
    """
    Ensure a single VRChat OSC connection exist
    """
    global _vrc
    if _vrc is None:
        logger.debug("first-time setup of VRChatOSC client")
        _vrc = VRChatOSC.connect()
    return _vrc


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


def close() -> None:
    """
    close the only Client
    """
    global _vrc
    if _vrc is not None:
        _vrc.close()
        _vrc = None
