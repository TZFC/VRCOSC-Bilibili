"""
An async accumulator consumer that sends decaying parameter updates to VRChatOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.
"""
import asyncio
import math
import logging
from app.Utils.constants import MAX_COUNT_PER_SECOND
from app.Utils.int2float8 import int2f8
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import set_parameter_value, parameter_names, parameter_default
from app.Utils.config_loader import CONFIG
logger = logging.getLogger(__name__)

timer_lcm: int = math.lcm(*CONFIG["set_parameter"]["parameter_decay_time"])


async def parameter_decay_loop() -> None:
    """
    Infinite loop that decays parameter toward default value
    """
    current_time: int = 0
    while True:
        await asyncio.sleep(1)
        current_time += 1
        if current_time == timer_lcm:
            current_time = 0
        for index, parameter_name in enumerate(parameter_names):
            decay_time: int = CONFIG["set_parameter"]["parameter_decay_time"][index]
            decay_value: int = CONFIG["set_parameter"]["parameter_decay_step"][index]
            current_value: int = set_parameter_value[parameter_name]
            default_value: int = parameter_default[index]
            if current_time % decay_time != 0:
                # 还没到汇报时间
                continue
            if current_value == default_value:
                # 无变化
                continue
            elif current_value > default_value:
                # 过大向下衰减
                current_value = max(default_value, current_value-decay_value)
                set_parameter_value[parameter_name] = current_value
                update_parameter(parameter_name, int2f8(current_value))
            else:
                # 过下向上衰退
                current_value = min(default_value, current_value+decay_value)
                set_parameter_value[parameter_name] = current_value
                update_parameter(parameter_name, int2f8(current_value))
