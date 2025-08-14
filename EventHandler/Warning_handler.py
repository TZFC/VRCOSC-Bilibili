"""
Warning handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from app.osc_queue import chatbox_queue
from app.config_loader import CONFIG
import logging
logger = logging.getLogger(__name__)


async def handle_warning(event: dict, update_chatbox: bool, update_osc_param: bool):
    text = event['data']['msg']
    if update_chatbox:
        await chatbox_queue.put(("警告：{text}", CONFIG["misc"]['warning_min_display_time']))
    # TODO: update params
