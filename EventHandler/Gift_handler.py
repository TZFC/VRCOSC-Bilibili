"""
Gift handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import asyncio


async def handle_gift(event: dict, update_chatbox: bool, update_osc_param: bool, osc_queue: asyncio.Queue):
    gift_name = event["data"]["data"]["giftName"]
    gift_num = event["data"]["data"]["num"]
    username = event["data"]["data"]["uname"]
    if update_chatbox:
        await osc_queue.put(("CHATBOX", f"{username}赠送{gift_num}个{gift_name}"))
    # TODO: update params
