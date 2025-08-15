"""
Danmaku emoticon handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from Utils.EVENT_IDX import *
from Utils.int2float8 import int2f8
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import chatbox_queue, general_gift_queue, animation_counts, set_parameter_value
from app.config_loader import CONFIG
import logging
logger = logging.getLogger(__name__)

send_all_emoticons = (CONFIG["filter_keywords"]
                      ["emoticon_chatbox_keywords"] == [])


async def handle_emoticon(event: dict, update_chatbox: bool, update_osc_param: bool):
    username = event["data"]["info"][USERINFO_IDX][USERINFO_USERNAME_IDX]
    text = event["data"]["info"][TEXT_IDX]
    if update_chatbox:
        if send_all_emoticons or (text in CONFIG["filter_keywords"]["emoticon_chatbox_keywords"]):
            await chatbox_queue.put((f"{username}:{text}", 0))
    if update_osc_param:
        if text in CONFIG["animation_accumulate"]["animation"]:  # 动画
            animation_counts[text] += 1
            logger.info("动画表情 %s", text)
        elif text in CONFIG["set_parameter"]["parameter_keywords"]:  # 变化
            set_index: int = CONFIG["set_parameter"]["parameter_keywords"].index(
                text)
            is_increase: bool = set_index % 2 == 0
            set_index = set_index // 2
            parameter_name: str = CONFIG["set_parameter"]["parameter_names"][set_index]
            step: int = CONFIG["set_parameter"]["parameter_increment"][set_index]
            if is_increase:
                set_parameter_value[parameter_name] += step * 1
            else:
                set_parameter_value[parameter_name] -= step * 1
            logger.info("变化表情 %s", text)
            update_parameter(parameter_name, int2f8(
                set_parameter_value[parameter_name]))
        else:  # 通用
            logger.info("通用表情 %s", text)
            await general_gift_queue.put((text, 1))
