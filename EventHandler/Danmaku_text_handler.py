"""
Danmaku text handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from Utils.EVENT_IDX import *
from app.config_loader import CONFIG
from app.osc_queue import chatbox_queue
import logging
logger = logging.getLogger(__name__)
send_all_text = (CONFIG['filter_keywords']['danmaku_chatbox_keywords'] == [])


async def handle_text(event: dict, update_chatbox: bool, update_osc_param: bool):
    username = event["data"]["info"][USERINFO_IDX][USERINFO_USERNAME_IDX]
    text = event["data"]["info"][TEXT_IDX]
    if update_chatbox:
        if send_all_text or any(key in text for key in CONFIG["filter_keywords"]["danmaku_chatbox_keywords"]):
            text = event["data"]["info"][TEXT_IDX]
            await chatbox_queue.put((text, 0))
    # TODO: update params
