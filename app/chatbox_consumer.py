"""
An async queue consumer that sends queued chatbox messages to VRChatOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.
"""
from app.osc.vrc_osc_singleton_client import send_chat
from app.osc_queue import chatbox_queue
import logging
import asyncio
logger = logging.getLogger(__name__)


async def chatbox_loop():
    while True:
        request = await chatbox_queue.get()
        logger.debug("收到聊天框请求 %s", str(request))
        try:
            text, min_display_time = request
            send_chat(text)
            logger.debug("聊天框请求 %s 成功, 还剩 %d 条请求", str(
                request), chatbox_queue.qsize())
            await asyncio.sleep(min_display_time)
        except Exception:
            logger.warning("聊天框请求 %s 发生错误, 忽略并继续", request)
        finally:
            chatbox_queue.task_done()
