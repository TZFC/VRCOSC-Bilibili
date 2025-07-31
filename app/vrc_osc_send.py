"""
An async queue consumer that sends queued messages to VRChatOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in THIRD_PARTY_NOTICES or the dependency's repository)

VRChat is a trademark of VRChat Inc.

Notes:
  - AI assistance was used in drafting parts of this file.
"""
import asyncio
from app.vrc_osc_singleton_client import update_parameter, send_chat, aclose
import logging
logger = logging.getLogger(__name__)


async def send_vrchat_osc(osc_queue: asyncio.Queue):
    while True:
        request = await osc_queue.get()
        try:
            request_type, args = request
            if request_type == "PARAMETER":
                name, value = args
                await update_parameter(name, value)
            elif request_type == "CHATBOX":
                message, immediate = args
                await send_chat(message, immediate)
            elif request_type == "STOP":
                await aclose()
            else:
                logger.warning("未知请求类型 %s", request_type)
            logger.info("请求 %s 成功, 还剩 %d 条请求", str(request),osc_queue.qsize())
        except:
            logger.warning("请求 %s 发生错误,忽略并继续", request)
        finally:
            osc_queue.task_done()
