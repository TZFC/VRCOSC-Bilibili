"""
Gift handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from app.config_loader import CONFIG
from app.osc_queue import chatbox_queue, general_gift_queue, animation_counts, set_parameter_value
from app.osc.vrc_osc_singleton_client import update_parameter
from Utils.int2float8 import int2f8
import logging
logger = logging.getLogger(__name__)


async def handle_gift(event: dict, update_chatbox: bool, update_osc_param: bool):
    gift_name: str = event["data"]["data"]["giftName"]
    gift_num: int = event["data"]["data"]["num"]
    username: str = event["data"]["data"]["uname"]
    if update_chatbox:
        await chatbox_queue.put((f"{username}赠送{gift_num}个{gift_name}", 0))
    if update_osc_param:
        if gift_name in CONFIG["animation_accumulate"]["animation"]:  # 动画礼物
            animation_counts[gift_name] += gift_num
        elif gift_name in CONFIG["set_parameter"]["parameter_keywords"]:  # 变化礼物
            set_index: int = CONFIG["set_parameter"]["parameter_keywords"].index(
                gift_name)
            is_increase: bool = set_index % 2 == 0
            set_index = set_index // 2
            parameter_name: str = CONFIG["set_parameter"]["parameter_names"][set_index]
            step: int = CONFIG["set_parameter"]["parameter_increment"][set_index]
            if is_increase:
                set_parameter_value[parameter_name] += step
            else:
                set_parameter_value[parameter_name] -= step
            update_parameter(parameter_name, int2f8(
                set_parameter_value[parameter_name]))

        else:  # 通用礼物
            await general_gift_queue.put((gift_name, gift_num))
