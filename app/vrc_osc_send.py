"""
An async queue consumer that sends queued messages to VRChatOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.

Notes:
  - AI assistance was used in drafting parts of this file.
"""
import asyncio
from app.osc.vrc_osc_singleton_client import update_parameter, send_chat, close
import logging
logger = logging.getLogger(__name__)


async def send_vrchat_osc(osc_queue: asyncio.Queue):
    while True:
        request = osc_queue.get()
        try:
            request_type, args = request
            if request_type == "PARAMETER":
                name, value = args
                update_parameter(name, value)
            elif request_type == "CHATBOX":
                message, immediate = args
                send_chat(message, immediate)
            elif request_type == "STOP":
                close()
            else:
                logger.warning("未知请求类型 %s", request_type)
            logger.info("请求 %s 成功, 还剩 %d 条请求", str(request),osc_queue.qsize())
        except:
            logger.warning("请求 %s 发生错误,忽略并继续", request)
        finally:
            osc_queue.task_done()
