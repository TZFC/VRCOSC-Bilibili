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
import asyncio
from app.osc.vrc_osc import VRChatOSC
import logging
logger = logging.getLogger(__name__)

_vrc: VRChatOSC = None
_lock = asyncio.Lock()


def _ensure_ready() -> VRChatOSC:
    global _vrc
    if _vrc is None:
        logger.debug("first time setup vrc client")
        with _lock:
            if _vrc is None:
                _vrc = VRChatOSC.connect()  # one client
    return _vrc


def update_parameter(name: str, value) -> None:
    logger.debug(f"preparing parameter update {name}, {value}")
    vrc = _ensure_ready()
    vrc.update_parameter(name, value)
    logger.debug(f"parameter updated {name}, {value}")


def send_chat(message: str, immediate: bool = True) -> None:
    logger.debug(f"preparing chat send {message}, {immediate}")
    vrc = _ensure_ready()
    vrc.send_chat(message, immediate)
    logger.debug(f"chat sent {message}, {immediate}")


def close() -> None:
    global _vrc
    logger.debug("closing VRChatOSC singleton Client")
    if _vrc is not None:
        _vrc.close()
        _vrc = None
