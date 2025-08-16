"""
Danmaku text handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from Data.EVENT_IDX import *
from app.Utils.config_loader import CONFIG
from app.Utils.int2float8 import int2f8
from app.Utils.name2id import name2id
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import chatbox_queue, general_gift_queue, animation_counts, set_parameter_value
import logging
logger = logging.getLogger(__name__)
send_all_text = (CONFIG['filter_keywords']['danmaku_chatbox_keywords'] == [])


async def handle_text(event: dict, update_chatbox: bool, update_osc_param: bool):
    # username: str = event["data"]["info"][USERINFO_IDX][USERINFO_USERNAME_IDX]
    text: str = event["data"]["info"][TEXT_IDX]
    if update_chatbox:
        if send_all_text or any(key in text for key in CONFIG["filter_keywords"]["danmaku_chatbox_keywords"]):
            await chatbox_queue.put((text, 0))
    if update_osc_param:
        if text in CONFIG["animation_accumulate"]["animation"]:  # 动画
            animation_counts[text] += 1
            logger.debug("动画弹幕 %s", text)
        elif text in CONFIG["set_parameter"]["parameter_keywords"]:  # 变化
            set_index: int = CONFIG["set_parameter"]["parameter_keywords"].index(
                text)
            is_increase: bool = set_index % 2 == 0
            set_index = set_index // 2
            parameter_name: str = CONFIG["set_parameter"]["parameter_names"][set_index]
            step: int = CONFIG["set_parameter"]["parameter_increment"][set_index]
            if is_increase:
                set_parameter_value[parameter_name] = min(set_parameter_value[parameter_name] + step * 1, 100)
            else:
                set_parameter_value[parameter_name] = max(set_parameter_value[parameter_name] - step * 1, 0)
            logger.debug("变化弹幕 %s", text)
            update_parameter(parameter_name, int2f8(
                set_parameter_value[parameter_name]))
        else:  # 通用
            logger.info("通用弹幕 %s", text)
            if text in CONFIG["filter_keywords"]["danmaku_parameter_keywords"]:
                danmaku_id: int = CONFIG["filter_keywords"]["danmaku_parameter_keywords"].index(
                    text)
                await general_gift_queue.put((name2id('TEXT'), danmaku_id))
