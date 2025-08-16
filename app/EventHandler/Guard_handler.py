"""
Guard handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from app.Utils.config_loader import CONFIG
from app.Utils.int2float8 import int2f8
from app.Utils.name2id import NAME_EVENT_ID, name2id
from app.osc.vrc_osc_singleton_client import update_parameter
from app.osc_queue import chatbox_queue, general_gift_queue, animation_counts, set_parameter_value
import logging
logger = logging.getLogger(__name__)


async def handle_guard(event: dict, update_chatbox: bool, update_osc_param: bool):
    username: str = event['data']['data']['username']
    guard_count: int = event['data']['data']['num']
    guard_level: int = event['data']['data']['guard_level']
    guard_name: str = event['data']['data']['gift_name']
    if update_chatbox:
        await chatbox_queue.put((f"{username}开通{guard_count}个月{guard_level}", CONFIG["misc"]["guard_min_display_time"]))
    if update_osc_param:
        guard_name = 'guard' + guard_name
        if guard_name in CONFIG["animation_accumulate"]["animation"]:  # 动画
            animation_counts[guard_name] += guard_count
            logger.info("动画舰长 %s", guard_name)
        elif guard_name in CONFIG["set_parameter"]["parameter_keywords"]:  # 变化
            set_index: int = CONFIG["set_parameter"]["parameter_keywords"].index(
                guard_name)
            is_increase: bool = set_index % 2 == 0
            set_index = set_index // 2
            parameter_name: str = CONFIG["set_parameter"]["parameter_names"][set_index]
            step: int = CONFIG["set_parameter"]["parameter_increment"][set_index]
            if is_increase:
                set_parameter_value[parameter_name] = min(set_parameter_value[parameter_name] + step * guard_count, 100)
            else:
                set_parameter_value[parameter_name] = max(set_parameter_value[parameter_name] - step * guard_count, 0)
            logger.info("变化舰长 %s", guard_name)
            update_parameter(parameter_name, int2f8(
                set_parameter_value[parameter_name]))
        else:  # 通用
            logger.info("通用舰长 %s", guard_name)
            if guard_name in NAME_EVENT_ID.keys():
                await general_gift_queue.put((name2id(guard_name), guard_count))
