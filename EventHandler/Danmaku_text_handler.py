"""
Danmaku text handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import asyncio
from Utils.EVENT_IDX import *
from app.config_loader import CONFIG
import logging
logger = logging.getLogger(__name__)
send_all_text = (CONFIG['danmaku_emoticon']['danmaku_key'] == [])


async def handle_text(event: dict, update_chatbox: bool, update_osc_param: bool, osc_queue: asyncio.Queue):
    username = event["data"]["info"][USERINFO_IDX][USERINFO_USERNAME_IDX]
    text = event["data"]["info"][TEXT_IDX]
    if update_chatbox:
        if send_all_text or any(key in text for key in CONFIG["danmaku_emoticon"]["danmaku_key"]):
            text = event["data"]["info"][TEXT_IDX]
            await osc_queue.put(("CHATBOX", text))
    # TODO: update params
