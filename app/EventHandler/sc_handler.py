"""
SC handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import logging
from app.Utils.int2float8 import int2f8
from app.Utils.name2id import NAME_EVENT_ID
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import chatbox_queue, general_gift_queue, animation_counts, set_parameter_value
from app.Utils.config_loader import CONFIG
logger = logging.getLogger(__name__)


async def handle_sc(event: dict, update_chatbox: bool, update_osc_param: bool):
    """
    handle super chat events
    """
    username: str = event['data']['data']['user_info']['uname']
    text: str = event['data']['data']['message']
    price: int = event['data']['data']['price']
    if update_chatbox:
        await chatbox_queue.put((f"{username}说{text}", CONFIG["misc"]['sc_min_display_time']))
    if update_osc_param:
        if 'sc' in CONFIG["animation_accumulate"]["animation"]:  # 动画
            animation_counts['sc'] += price
            logger.info("动画sc %s", 'sc')
        elif 'sc' in CONFIG["set_parameter"]["parameter_keywords"]:  # 变化
            set_index: int = CONFIG["set_parameter"]["parameter_keywords"].index(
                'sc')
            is_increase: bool = set_index % 2 == 0
            set_index = set_index // 2
            parameter_name: str = CONFIG["set_parameter"]["parameter_names"][set_index]
            step: int = CONFIG["set_parameter"]["parameter_increment"][set_index]
            if is_increase:
                set_parameter_value[parameter_name] = min(
                    set_parameter_value[parameter_name] + step * price, 100)
            else:
                set_parameter_value[parameter_name] = max(
                    set_parameter_value[parameter_name] - step * price, 0)
            logger.info("变化sc %s", 'sc')
            update_parameter(parameter_name, int2f8(
                set_parameter_value[parameter_name]))
        else:  # 通用
            logger.info("通用sc %s 元", str(price))
            await general_gift_queue.put((NAME_EVENT_ID['SC'], price))
