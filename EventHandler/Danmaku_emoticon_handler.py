"""
Danmaku emoticon handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import asyncio
from Utils.EVENT_IDX import *


async def handle_emoticon(event: dict, update_chatbox: bool, update_osc_param: bool, osc_queue: asyncio.Queue):
    username = event["data"]["info"][USERINFO_IDX][USERINFO_USERNAME_IDX]
    text = event["data"]["info"][TEXT_IDX]
    if update_chatbox:
        await osc_queue.put(("CHATBOX", f"{username}:{text}"))
    # TODO: update params
