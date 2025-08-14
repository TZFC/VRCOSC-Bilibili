"""
SC handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import asyncio


async def handle_sc(event: dict, update_chatbox: bool, update_osc_param: bool, osc_queue: asyncio.Queue):
    username = event['data']['data']['user_info']['uname']
    text = event['data']['data']['message']
    if update_chatbox:
        await osc_queue.put(('CHATBOX', f"{username}说{text}"))
    # TODO: updata params
