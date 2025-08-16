"""
An async accumulator consumer that sends accumulated animation controller parameter updates to VRChatOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.
"""
from Data.EVENT_IDX import MAX_COUNT_PER_SECOND
from app.Utils.int2float8 import int2f8
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import animation_counts
from app.Utils.config_loader import CONFIG
import asyncio
import math
import logging
logger = logging.getLogger(__name__)

timer_lcm: int = math.lcm(*CONFIG["animation_accumulate"]["animation_time"])


async def animation_loop():
    current_time: int = 0
    while True:
        await asyncio.sleep(1)
        current_time += 1
        if current_time == timer_lcm:
            current_time = 0
        for index, (animation_name, pending_value) in enumerate(animation_counts.items()):
            animation_time: int = CONFIG["animation_accumulate"]["animation_time"][index]
            if current_time % animation_time != 0:
                # 还没到汇报时间
                continue
            if pending_value >= MAX_COUNT_PER_SECOND:
                # 堆积超过上限，汇报上限
                update_parameter(animation_name, int2f8(MAX_COUNT_PER_SECOND))
                animation_counts[animation_name] -= MAX_COUNT_PER_SECOND
            elif pending_value > 0:
                # 堆积不足上限，汇报所有堆积
                update_parameter(animation_name, int2f8(pending_value))
                animation_counts[animation_name] = 0
            else:
                # 无堆积，归零
                update_parameter(animation_name, 0)
                animation_counts[animation_name] = 0
