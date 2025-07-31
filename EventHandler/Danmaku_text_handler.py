"""
Main event dispatcher from Bilibili danmaku stream events to event handlers

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - bilibili-api-python (see its license in the dependency's repository)

BILIBILI is a trademark of Shanghai Hode Information Technology Co., Ltd.
"""
import asyncio
from Utils.EVENT_IDX import *
from app.config_loader import CONFIG
import logging
logger = logging.getLogger(__name__)
send_all_text = (CONFIG['danmaku_key'] == [])

async def handle_text(event: dict, update_chatbox: bool, update_osc_param: bool, osc_queue: asyncio.Queue):
    if update_chatbox:
        text = event["data"]["info"][TEXT_IDX]
        osc_queue.put(("CHATBOX", text))
