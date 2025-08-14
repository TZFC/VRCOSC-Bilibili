"""
An async queue consumer that sends accumulated animation controller parameter updates to VRChatOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.
"""
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import animation_counts
from app.config_loader import CONFIG
import asyncio
import math
import logging
logger = logging.getLogger(__name__)

timer_lcm = math.lcm(*CONFIG["animation_accumulate"]["animation_time"])


async def animation_loop():
    current_time = 0
    while True:
        await asyncio.sleep(1)
        current_time += 1
        if current_time == timer_lcm:
            current_time = 0
        # TODO: iterate over animation updates
