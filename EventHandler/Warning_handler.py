"""
Warning handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import asyncio


async def handle_warning(event: dict, update_chatbox: bool, update_osc_param: bool, osc_queue: asyncio.Queue):
    text = event['data']['msg']
    if update_chatbox:
        await osc_queue.put(("CHATBOX", "警告：{text}"))
    # TODO: update params
