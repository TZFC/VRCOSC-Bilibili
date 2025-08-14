"""
SC handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
from app.osc_queue import chatbox_queue
from app.config_loader import CONFIG
import logging
logger = logging.getLogger(__name__)


async def handle_sc(event: dict, update_chatbox: bool, update_osc_param: bool):
    username = event['data']['data']['user_info']['uname']
    text = event['data']['data']['message']
    if update_chatbox:
        await chatbox_queue.put((f"{username}说{text}", CONFIG["misc"]['sc_min_display_time']))
    # TODO: updata params
