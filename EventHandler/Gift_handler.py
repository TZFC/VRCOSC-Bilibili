"""
Gift handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from app.config_loader import CONFIG
from app.osc_queue import chatbox_queue, general_gift_queue, animation_counts
import logging
logger = logging.getLogger(__name__)

async def handle_gift(event: dict, update_chatbox: bool, update_osc_param: bool):
    gift_name = event["data"]["data"]["giftName"]
    gift_num = event["data"]["data"]["num"]
    username = event["data"]["data"]["uname"]
    if update_chatbox:
        await chatbox_queue.put(f"{username}赠送{gift_num}个{gift_name}")
    if update_osc_param:
        if gift_name in CONFIG["animation_accumulate"]["animation"]:  # 独立礼物
            animation_counts[gift_name] += gift_num
        else:  # 通用礼物
            await general_gift_queue.put((gift_name, gift_num))
