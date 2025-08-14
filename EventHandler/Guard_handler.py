"""
Guard handler

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).
"""
import asyncio


async def handle_guard(event: dict, update_chatbox: bool, update_osc_param: bool, osc_queue: asyncio.Queue):
    username = event['data']['data']['username']
    guard_count = event['data']['data']['num']
    guard_level = event['data']['data']['guard_level']
    guard_name = event['data']['data']['gift_name']
    if update_chatbox:
        await osc_queue.put(("CHATBOX", f"{username}开通{guard_count}个月{guard_level}"))
    # TODO: update params
