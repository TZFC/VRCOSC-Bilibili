"""
A singleton VRChatOSC API

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in THIRD_PARTY_NOTICES or the dependency's repository)

VRChat is a trademark of VRChat Inc.

Notes:
  - AI assistance was used in drafting parts of this file.
"""
import asyncio
from vrc_osc import VRChatOSC
import logging
logger = logging.getLogger(__name__)

_vrc: VRChatOSC = None
_lock = asyncio.Lock()


async def _ensure_ready() -> VRChatOSC:
    global _vrc
    if _vrc is None:
        logger.debug("first time setup vrc client")
        async with _lock:
            if _vrc is None:
                _vrc = await VRChatOSC.connect()  # one client
    return _vrc


async def update_parameter(name: str, value) -> None:
    logger.debug(f"preparing parameter update {name}, {value}")
    vrc = await _ensure_ready()
    await vrc.update_parameter(name, value)
    logger.debug(f"parameter updated {name}, {value}")


async def send_chat(message: str, immediate: bool = True) -> None:
    logger.debug(f"preparing chat send {message}, {immediate}")
    vrc = await _ensure_ready()
    await vrc.send_chat(message, immediate)
    logger.debug(f"chat sent {message}, {immediate}")


async def aclose() -> None:
    global _vrc
    logger.debug("closing VRChatOSC singleton Client")
    if _vrc is not None:
        await _vrc.aclose()
        _vrc = None
