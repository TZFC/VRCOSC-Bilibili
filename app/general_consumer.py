"""
An async queue consumer that sends queued parameter updates to VRChatOSC

Copyright (C) 2025  TZFC <tianzifangchen@gmail.com>
License: GNU General Public License v3.0 or later (see LICENSE).

Dependencies:
  - python-osc (see its license in the dependency's repository)

VRChat is a trademark of VRChat Inc.
"""
import asyncio
import logging
from app.Utils.int2float8 import int2f8
from app.osc_queue import general_gift_queue
from app.osc.vrc_osc_singleton_client import update_parameter
logger = logging.getLogger(__name__)


async def general_loop():
    """
    Infinite loop that consumes from general_gift_queue
    """
    while True:
        request: tuple[int, int] = await general_gift_queue.get()
        logger.debug("收到通用请求 %s", str(request))
        try:
            event_id, event_num = request
            update_parameter('event_id', event_id)
            update_parameter('event_num', int2f8(event_num))
            logger.debug("通用请求 %s 成功, 还剩 %d 条请求", str(
                request), general_gift_queue.qsize())
        except asyncio.CancelledError:
            logger.debug("General loop cancelled")
            raise
        except (IndexError, KeyError, TypeError, ValueError) as e:
            logger.error("通用请求 %s 发生错误 %s, 忽略并继续", str(request), str(e))
            logger.debug("通用请求解析失败: %s", request, exc_info=True)
        finally:
            general_gift_queue.task_done()
