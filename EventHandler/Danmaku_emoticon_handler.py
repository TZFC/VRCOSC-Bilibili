"""
Danmaku emoticon handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from Utils.EVENT_IDX import *
from app.osc_queue import chatbox_queue
from app.config_loader import CONFIG
import logging
logger = logging.getLogger(__name__)

send_all_emoticons = (CONFIG["filter_keywords"]["emoticon_chatbox_keywords"] == [])

async def handle_emoticon(event: dict, update_chatbox: bool, update_osc_param: bool):
    username = event["data"]["info"][USERINFO_IDX][USERINFO_USERNAME_IDX]
    text = event["data"]["info"][TEXT_IDX]
    if update_chatbox:
        if send_all_emoticons or (text in CONFIG["filter_keywords"]["emoticon_chatbox_keywords"]):
            await chatbox_queue.put((f"{username}:{text}", 0))
    if update_osc_param:
        if text in CONFIG["filter_keywords"]["emoticon_parameter_keywords"]:
            # drive parameters here
            pass 